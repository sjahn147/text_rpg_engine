"""
gameplay 라우터 import 테스트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

os.chdir(project_root)

try:
    print("1. gameplay 모듈 import 시도...")
    from app.ui.backend.routes import gameplay
    print("   ✅ Import 성공!")
    
    print(f"\n2. Router 정보:")
    print(f"   Prefix: {gameplay.router.prefix}")
    print(f"   Tags: {gameplay.router.tags}")
    
    print(f"\n3. 등록된 라우트:")
    routes = []
    for route in gameplay.router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                'path': route.path,
                'methods': list(route.methods),
                'name': getattr(route, 'name', 'N/A')
            })
    
    interact_routes = [r for r in routes if 'interact' in r['path']]
    print(f"   총 {len(routes)}개 라우트 중 'interact' 관련: {len(interact_routes)}개")
    for route in interact_routes:
        print(f"   - {route['methods']} {route['path']} ({route['name']})")
    
    print(f"\n4. main.py에서 router 등록 테스트...")
    from app.ui.backend.main import app
    print("   ✅ app import 성공!")
    
    # app에 등록된 라우트 확인
    app_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            app_routes.append({
                'path': route.path,
                'methods': list(route.methods)
            })
    
    interact_app_routes = [r for r in app_routes if 'interact' in r['path']]
    print(f"   app에 등록된 총 {len(app_routes)}개 라우트 중 'interact' 관련: {len(interact_app_routes)}개")
    for route in interact_app_routes:
        print(f"   - {route['methods']} {route['path']}")
    
    if len(interact_app_routes) == 0:
        print("\n   ❌ 문제 발견: app에 interact 라우트가 등록되지 않았습니다!")
    else:
        print("\n   ✅ app에 interact 라우트가 정상적으로 등록되었습니다!")
        
except ImportError as e:
    print(f"   ❌ Import 실패: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"   ❌ 에러: {e}")
    import traceback
    traceback.print_exc()

