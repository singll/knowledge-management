"""应用启动入口"""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("="*60)
    print("Knowledge Management System Backend")
    print(f"Server: http://{host}:{port}")
    print(f"Health: http://{host}:{port}/health")
    print("="*60)
    
    app.run(host=host, port=port, debug=debug)
