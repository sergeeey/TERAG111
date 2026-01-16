"""
Telegram service for TERAG:
- sends scheduled daily cognitive report
- accepts commands to run missions, request status, perform quick searches
- protects access with a whitelist
"""

import os
import asyncio
import logging
import json
import shlex
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from aiogram import Bot, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import httpx

# Load .env
load_dotenv()  # reads .env in project root

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # default chat for pushes
WHITELIST = os.getenv("TELEGRAM_WHITELIST", "")  # comma separated user ids
WHITELIST_IDS = {int(x.strip()) for x in WHITELIST.split(",") if x.strip().isdigit()}

# Config
DAILY_REPORT_HOUR = int(os.getenv("TERAG_DAILY_REPORT_HOUR", "9"))  # server local time
DAILY_REPORT_MINUTE = int(os.getenv("TERAG_DAILY_REPORT_MINUTE", "0"))
MAX_CONCURRENT_MISSIONS = int(os.getenv("TERAG_MAX_CONCURRENT_MISSIONS", "3"))
MISSION_RUNNER_CMD = os.getenv("TERAG_MISSION_RUNNER", "python installer/start_mission.py")
HEALTH_CHECK_CMD = os.getenv("TERAG_HEALTHCHECK_CMD", "python check_terag_full_stack.py")

logger = logging.getLogger("telegram_service")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in .env")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

scheduler = AsyncIOScheduler()
concurrent_missions = set()  # track running mission ids (simple)

# -------------------------
# Helpers
# -------------------------

def is_authorized(user_id: int) -> bool:
    # allow if whitelist empty (development), otherwise check presence
    if not WHITELIST_IDS:
        return True
    return user_id in WHITELIST_IDS

async def run_subprocess(cmd: str, timeout: int = 300) -> dict:
    """Run a shell command and return dict with status, output, code."""
    try:
        # secure split
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            return {"ok": False, "error": "timeout", "code": -1}
        out = stdout.decode(errors="ignore")
        err = stderr.decode(errors="ignore")
        return {"ok": proc.returncode == 0, "code": proc.returncode, "out": out, "err": err}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def load_health_json(path: str = "terag_health_check.json") -> Optional[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def format_health_short(health_json: dict) -> str:
    lines = ["🧠 *TERAG Status*"]
    for k, v in health_json.items():
        if k in ("timestamp", "overall_status"):
            continue
        status = v.get("status", "unknown")
        emoji = "✅" if status == "success" else ("⚠️" if status == "skipped" else "❌")
        lines.append(f"{emoji} {k}: {status}")
    return "\n".join(lines)

def format_health_pretty(health_json: dict) -> str:
    ts = health_json.get("timestamp", datetime.utcnow().isoformat())
    lines = [f"🧠 *TERAG Cognitive Ops Report* — {ts}", ""]
    for comp in ("lm_studio", "brave_search", "bright_data", "neo4j", "integration"):
        v = health_json.get(comp, {})
        st = v.get("status", "unknown")
        emoji = "✅" if st == "success" else ("⚠️" if st == "skipped" else "❌")
        details = []
        # add summary details
        if "latency" in v:
            details.append(f"latency={v['latency']:.2f}s")
        if "models" in v:
            details.append(f"models={len(v['models'])}")
        if "nodes_count" in v and v["nodes_count"] is not None:
            details.append(f"nodes={v['nodes_count']}")
        detail_line = (": " + ", ".join(details)) if details else ""
        lines.append(f"{emoji} {comp}{detail_line}")
    lines.append("")
    lines.append("• To run mission: /run_mission <mission_name>")
    lines.append("• To do a quick find: /find <query>")
    lines.append("• To run deep search: /deep_search <query>")
    return "\n".join(lines)

# -------------------------
# Command handlers
# -------------------------

@dp.message(Command(commands=["start", "help"]))
async def cmd_start(message: Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ Unauthorized user.")
        return
    txt = (
        "🤖 *TERAG Bot at your service.*\n\n"
        "*Commands:*\n"
        "/status — quick status\n"
        "/health — full health report\n"
        "/run_mission <name> — run mission by name\n"
        "/find <query> — quick OSINT search\n"
        "/deep_search <query> — run full mission for query\n"
        "/cancel <task_id> — cancel mission (if possible)\n"
    )
    await message.reply(txt, parse_mode="Markdown")

@dp.message(Command(commands=["status"]))
async def cmd_status(message: Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ Unauthorized")
        return
    # run quick health check (non-blocking call to script)
    res = await run_subprocess(HEALTH_CHECK_CMD, timeout=20)
    if res.get("ok"):
        # try load JSON (script saves to file)
        data = await load_health_json()
        if data:
            await message.reply(format_health_short(data), parse_mode="Markdown")
            return
        await message.reply("✅ Health check completed (no JSON):\n" + res.get("out", "")[:1000])
        return
    await message.reply(f"❌ Health check failed: {res.get('err') or res.get('error', '')}")

@dp.message(Command(commands=["health"]))
async def cmd_health(message: Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ Unauthorized")
        return
    # run full healthcheck (may take longer)
    await message.reply("🔄 Running full health-check (this may take up to 2 minutes)...")
    res = await run_subprocess(HEALTH_CHECK_CMD, timeout=180)
    if not res.get("ok"):
        await message.reply("❌ Health check failed: " + (res.get("err") or str(res.get("error"))))
        return
    data = await load_health_json()
    if data:
        await message.reply(format_health_pretty(data), parse_mode="Markdown")
    else:
        await message.reply("✅ Health check finished. No JSON report available.", parse_mode="Markdown")

async def send_fact_notification(fact: Dict[str, Any], source: str = "", confidence: float = 0.0):
    """Отправить уведомление о новом факте в графе"""
    if not TELEGRAM_CHAT_ID:
        return
    
    try:
        subject = fact.get("subject", "")
        predicate = fact.get("predicate", "RELATED_TO")
        obj = fact.get("object", "")
        
        message_text = f"""🧩 *Новый факт добавлен в граф*

*{subject}* -[{predicate}]-> *{obj}*

Confidence: {confidence:.2f}
Source: {source[:50] if source else 'N/A'}"""
        
        await bot.send_message(TELEGRAM_CHAT_ID, message_text, parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"Could not send fact notification: {e}")

def send_fact_notification_sync(fact: Dict[str, Any], source: str = "", confidence: float = 0.0):
    """Синхронная обёртка для отправки уведомления о факте"""
    try:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Если loop уже запущен, создаём задачу
                asyncio.create_task(send_fact_notification(fact, source, confidence))
            else:
                loop.run_until_complete(send_fact_notification(fact, source, confidence))
        except RuntimeError:
            # Если нет event loop, создаём новый
            asyncio.run(send_fact_notification(fact, source, confidence))
    except Exception as e:
        logger.debug(f"Could not send Telegram notification: {e}")

async def send_pattern_notification(pattern: Dict[str, Any]):
    """Отправить уведомление о новом паттерне"""
    if not TELEGRAM_CHAT_ID:
        return
    
    try:
        pattern_name = pattern.get("pattern_name", "Unknown")
        classification = pattern.get("classification", "UNKNOWN")
        reason = pattern.get("reason", "")[:200]
        
        emoji = "🟢" if classification == "SUCCESS" else "🔴"
        
        message_text = f"""🧩 *Новый паттерн: {pattern_name}*

{emoji} Классификация: *{classification}*

🔍 Причина: {reason}"""
        
        await bot.send_message(TELEGRAM_CHAT_ID, message_text, parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"Could not send pattern notification: {e}")

def send_pattern_notification_sync(pattern: Dict[str, Any]):
    """Синхронная обёртка для отправки уведомления о паттерне"""
    try:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(send_pattern_notification(pattern))
            else:
                loop.run_until_complete(send_pattern_notification(pattern))
        except RuntimeError:
            asyncio.run(send_pattern_notification(pattern))
    except Exception as e:
        logger.debug(f"Could not send pattern notification: {e}")

@dp.message(Command(commands=["run_mission"]))
async def cmd_run_mission(message: Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ Unauthorized")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) == 1:
        await message.reply("Usage: /run_mission <mission_name>")
        return
    mission_name = parts[1].strip()
    
    # protect concurrency
    if len(concurrent_missions) >= MAX_CONCURRENT_MISSIONS:
        await message.reply("⚠️ Too many missions running. Try later.")
        return
    
    # run mission via subprocess
    await message.reply(f"▶️ Launching mission `{mission_name}` ...", parse_mode="Markdown")
    
    async def _run():
        concurrent_missions.add(mission_name)
        try:
            # Find mission file
            mission_path = None
            missions_dir = Path("installer/data")
            possible_names = [
                f"{mission_name}.yaml",
                f"mission_{mission_name}.yaml",
                f"{mission_name}.yml"
            ]
            
            for name in possible_names:
                candidate = missions_dir / name
                if candidate.exists():
                    mission_path = candidate
                    break
            
            if not mission_path:
                await bot.send_message(message.chat.id, f"❌ Mission `{mission_name}` not found in {missions_dir}")
                return
            
            cmd = f"{MISSION_RUNNER_CMD} {shlex.quote(str(mission_path))}"
            r = await run_subprocess(cmd, timeout=60*30)  # 30 minutes max
            
            if r.get("ok"):
                output = r.get("out", "")[:2000]
                await bot.send_message(
                    message.chat.id,
                    f"✅ Mission `{mission_name}` finished.\n\n*Output:*\n```\n{output}\n```",
                    parse_mode="Markdown"
                )
            else:
                await bot.send_message(
                    message.chat.id,
                    f"❌ Mission `{mission_name}` failed: {r.get('err') or r.get('error')}",
                    parse_mode="Markdown"
                )
        finally:
            concurrent_missions.discard(mission_name)
    
    asyncio.create_task(_run())

@dp.message(Command(commands=["find"]))
async def cmd_find(message: Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ Unauthorized")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) == 1:
        await message.reply("Usage: /find <query>")
        return
    query = parts[1].strip()
    
    await message.reply(f"🔎 Quick search for: `{query}` (this returns a few top results)", parse_mode="Markdown")
    
    # quick search via Brave API (lightweight)
    brave_key = os.getenv("BRAVE_API_KEY")
    if not brave_key:
        await message.reply("⚠️ Brave API key not set.")
        return
    
    url = "https://api.search.brave.com/res/v1/web/search"
    params = {"q": query, "count": 3}
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": brave_key
    }
    
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            r = await client.get(url, params=params, headers=headers)
            r.raise_for_status()
            data = r.json()
            hits = data.get("web", {}).get("results", [])
            
            if not hits:
                await message.reply("No results found.")
                return
            
            msg = "*Top results:*\n\n"
            for h in hits:
                title = h.get("title", "No title")
                link = h.get("url", "")
                snippet = h.get("description", h.get("snippet", ""))
                msg += f"• [{title}]({link})\n{snippet[:200]}...\n\n"
            
            await message.reply(msg, parse_mode="Markdown", disable_web_page_preview=True)
        except Exception as e:
            await message.reply(f"❌ Error querying Brave: {str(e)}")

@dp.message(Command(commands=["deep_search"]))
async def cmd_deep_search(message: Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ Unauthorized")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) == 1:
        await message.reply("Usage: /deep_search <query>")
        return
    query = parts[1].strip()
    
    await message.reply(f"🔎 Launching deep search mission for: `{query}`", parse_mode="Markdown")
    
    # Kick off a mission — create mission yaml and run mission runner
    mission_name = f"deep_search_{int(datetime.utcnow().timestamp())}"
    
    # create a simple mission YAML file inside missions/ by convention
    mission_yaml = f"""mission:
  name: "{mission_name}"
  schedule: "manual"
  steps:
    - name: collect_brave_data
      module: brave_extractor
      query: "{query}"
      output: "{mission_name}_raw.json"
    - name: analyze_data
      module: bright_analyzer
      input: "{mission_name}_raw.json"
      output: "{mission_name}_insights.json"
    - name: update_graph
      module: graph_updater
      input: "{mission_name}_insights.json"
      update_mode: append
"""
    
    missions_dir = Path("missions")
    missions_dir.mkdir(exist_ok=True)
    mission_path = missions_dir / f"{mission_name}.yaml"
    
    with open(mission_path, "w", encoding="utf-8") as f:
        f.write(mission_yaml)
    
    # start mission
    async def _run():
        concurrent_missions.add(mission_name)
        try:
            cmd = f"{MISSION_RUNNER_CMD} {shlex.quote(str(mission_path))}"
            r = await run_subprocess(cmd, timeout=60*60)  # allow up to 60 minutes
            
            if r.get("ok"):
                await bot.send_message(message.chat.id, f"✅ Deep search `{mission_name}` finished.")
            else:
                await bot.send_message(message.chat.id, f"❌ Deep search `{mission_name}` failed: {r.get('err') or r.get('error')}")
        finally:
            concurrent_missions.discard(mission_name)
    
    asyncio.create_task(_run())

@dp.message(Command(commands=["cancel"]))
async def cmd_cancel(message: Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ Unauthorized")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) == 1:
        await message.reply("Usage: /cancel <mission_name>")
        return
    mission_name = parts[1].strip()
    
    # best-effort: if running process exists we can't reliably kill here unless we store pids
    # inform user that cancellation attempted
    if mission_name in concurrent_missions:
        # cancellation not implemented robustly — we'll signal user
        await message.reply(f"⚠️ Cancellation requested for `{mission_name}`. If supported, runner will be asked to stop.")
    else:
        await message.reply("No such running mission found.")

# -------------------------
# Scheduled daily report
# -------------------------

async def send_daily_report():
    # prepare health-check using script, then send pretty report
    try:
        await bot.send_message(TELEGRAM_CHAT_ID, "⏳ Preparing daily TERAG report...")
    except Exception:
        # fallback: try to find last interaction chat or abort
        pass
    
    res = await run_subprocess(HEALTH_CHECK_CMD, timeout=180)
    data = await load_health_json()
    
    # Generate OSINT digest
    try:
        from src.integration.osint_digest import generate_daily_digest
        digest = generate_daily_digest()
    except Exception as e:
        logger.warning(f"Could not generate OSINT digest: {e}")
        digest = None
    
    # Generate system context snapshot
    try:
        from src.core.system_context import SystemContext
        system_ctx = SystemContext()
        system_snapshot = system_ctx.format_for_telegram()
        # Save snapshot to file
        system_ctx.save_to_file()
    except Exception as e:
        logger.warning(f"Could not generate system context: {e}")
        system_snapshot = None
    
    # Format main report
    if data:
        text = format_health_pretty(data)
        
        # Add OSINT digest if available
        if digest:
            text += "\n\n" + digest
        
        # Add system context if available
        if system_snapshot:
            text += "\n\n" + system_snapshot
        
        await bot.send_message(TELEGRAM_CHAT_ID, text, parse_mode="Markdown")
    else:
        # send raw if no JSON
        message = "Daily health-check completed, but no JSON found. Raw output:\n" + (res.get("out")[:4000] if res else "no output")
        
        # Add digest even if no health JSON
        if digest:
            message += "\n\n" + digest
        
        # Add system context
        if system_snapshot:
            message += "\n\n" + system_snapshot
        
        await bot.send_message(TELEGRAM_CHAT_ID, message, parse_mode="Markdown")

def schedule_daily_report():
    scheduler.add_job(
        send_daily_report,
        'cron',
        hour=DAILY_REPORT_HOUR,
        minute=DAILY_REPORT_MINUTE,
        id="daily_report",
        replace_existing=True
    )
    scheduler.start()

# -------------------------
# Runner
# -------------------------

async def main():
    # start scheduler
    schedule_daily_report()
    logger.info(f"Daily report scheduled for {DAILY_REPORT_HOUR}:{DAILY_REPORT_MINUTE:02d}")
    
    # start bot polling
    try:
        logger.info("Starting Telegram bot...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

