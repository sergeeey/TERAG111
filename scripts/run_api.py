import os, sys, uvicorn
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == '__main__':
    port = int(os.getenv('PORT','8000'))
    uvicorn.run('src.api.server:app', host='0.0.0.0', port=port, reload=True)
