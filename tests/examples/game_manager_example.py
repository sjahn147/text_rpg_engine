# 게임 매니저 초기화
game_manager = GameManager()

# 새 게임 시작
session_id = game_manager.start_new_game('HUMAN_WARRIOR_001')

# 특정 셀 로드 (상점 방문)
cell_contents = game_manager.load_cell_contents('CELL_SHOP_WEAPON_001')

# NPC와 대화 시작
interaction_result = game_manager.handle_interaction(
    player_entity_id,  # UUID
    shop_keeper_id,    # UUID
    'DIALOGUE',
    {'context_id': 'SHOP_GREETING_1'}
)

# 플레이어의 선택 처리
choice_result = game_manager.process_player_choice(
    event_id,          # UUID
    'TRADE_ACCEPT',
    {
        'buyer_id': player_entity_id,
        'seller_id': shop_keeper_id,
        'items': ['WEAPON_SWORD_NORMAL_001'],
        'price': 100
    }
)