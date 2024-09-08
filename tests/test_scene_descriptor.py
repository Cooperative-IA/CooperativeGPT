
from game_environment.scene_descriptor.scene_descriptor import SceneDescriptor

def test_describe_scene_commons_harvest(mocker):
    # Test that an agent who zapped another agent is detected
    substrate_config = mocker.MagicMock()
    substrate_config.lab2d_settings.numPlayers = 3
    substrate_config.player_names = ['player1', 'player2', 'player3']
    substrate_config.lab2d_settings.simulation.gameObjects = [{"name": "avatar", "components": [
        {
            "component": "Avatar",
            "kwargs": {
                "view": {'left': 5, 'right': 5, 'forward': 9, 'backward': 1, 'centered': False},
            }
        }
    ]}, {"name": "avatar", "components": [
        {
            "component": "Avatar",
            "kwargs": {
                "view": {'left': 5, 'right': 5, 'forward': 9, 'backward': 1, 'centered': False},
            }
        }
    ]}, {"name": "avatar", "components": [
        {
            "component": "Avatar",
            "kwargs": {
                "view": {'left': 5, 'right': 5, 'forward': 9, 'backward': 1, 'centered': False},
            }
        }
    ]}]
    scene_descriptor = SceneDescriptor(substrate_config, 'commons_harvest_open')

    # First set that there is a murderer
    timestep = mocker.MagicMock()
    globalmap = mocker.MagicMock()
    mapitem = mocker.MagicMock(**{
        "decode.return_value": "WWWWWWWWWWWWWW\nWWWWWWWWWWWWWW\nWWWWWWWWWWWWWW\nWWWWWWWWWWWWWW\nWWWWWWWWWWWWWW\nWWWWWWWWWWWWWW\nWWWWWWWWWWWWWW"
    })
    globalmap.configure_mock(**{
        "item.return_value": mapitem
    }
    )
    timestep.observation = {
        "GLOBAL.TEXT": globalmap,
        "WORLD.RGB": "WORLD.RGB",
        "1.RGB": "1.RGB",
        "2.RGB": "2.RGB",
        "3.RGB": "3.RGB",
        "1.POSITION": [2, 2],
        "2.POSITION": [2, 3],
        "3.POSITION": [4, 4],
        "1.ORIENTATION": 0,
        "2.ORIENTATION": 3,
        "3.ORIENTATION": 1,
        "1.REWARD": 0,
        "2.REWARD": 0,
        "3.REWARD": 0,
        "WORLD.WHO_ZAPPED_WHO": [[0, 1, 0], [0, 0, 0], [0, 0, 0]], # Rows represent the victim index, and columns represent the murderer
        "WORLD.AVATAR_STATES": [1, 1, 1] # At first all the avatars are alive
    }
    scene_description, curr_map = scene_descriptor.describe_scene(timestep)
    
    assert scene_descriptor.avatars[0].murder == 'player2', "The murder attribute of the first avatar should be set to player 2"
    assert scene_descriptor.avatars[1].murder == None, "The murder attribute of the second avatar should be set to player 2"
    assert scene_descriptor.avatars[2].murder == None, "The murder attribute of the first avatar should be set to player 2"

    assert scene_description['player1']['effective_zap'] == False, "The 'effective_zap' observation for player1 should be False"
    assert scene_description['player2']['effective_zap'] == False, "The 'effective_zap' observation for player2 should be False"
    assert scene_description['player3']['effective_zap'] == False, "The 'effective_zap' observation for player3 should be False"

    # Then test that when the agent attacked is dead the flag of "effective_zap" is set
    timestep.observation = {
        "GLOBAL.TEXT": globalmap,
        "WORLD.RGB": "WORLD.RGB",
        "1.RGB": "1.RGB",
        "2.RGB": "2.RGB",
        "3.RGB": "3.RGB",
        "1.POSITION": [2, 2],
        "2.POSITION": [2, 3],
        "3.POSITION": [4, 4],
        "1.ORIENTATION": 0,
        "2.ORIENTATION": 3,
        "3.ORIENTATION": 1,
        "1.REWARD": 0,
        "2.REWARD": 0,
        "3.REWARD": 0,
        "WORLD.WHO_ZAPPED_WHO": [[0, 1, 0], [0, 0, 0], [0, 0, 0]], # Rows represent the victim index, and columns represent the murderer
        "WORLD.AVATAR_STATES": [0, 1, 1] # Now the first avatar is actually dead
    }
    scene_description, curr_map = scene_descriptor.describe_scene(timestep)

    assert scene_description['player1']['effective_zap'] == False, "The 'effective_zap' observation for player1 should be False"
    assert scene_description['player2']['effective_zap'] == True, "The 'effective_zap' observation for player2 should be True"
    assert scene_description['player3']['effective_zap'] == False, "The 'effective_zap' observation for player3 should be False"

    # Finally the 'effective_zap' should be reseted
    timestep.observation = {
        "GLOBAL.TEXT": globalmap,
        "WORLD.RGB": "WORLD.RGB",
        "1.RGB": "1.RGB",
        "2.RGB": "2.RGB",
        "3.RGB": "3.RGB",
        "1.POSITION": [2, 2],
        "2.POSITION": [2, 3],
        "3.POSITION": [4, 4],
        "1.ORIENTATION": 0,
        "2.ORIENTATION": 3,
        "3.ORIENTATION": 1,
        "1.REWARD": 0,
        "2.REWARD": 0,
        "3.REWARD": 0,
        "WORLD.WHO_ZAPPED_WHO": [[0, 0, 0], [0, 0, 0], [0, 0, 0]], # Now zaps registered
        "WORLD.AVATAR_STATES": [0, 1, 1] # The first avatar is still death
    }
    scene_description, curr_map = scene_descriptor.describe_scene(timestep)

    assert scene_description['player1']['effective_zap'] == False, "The 'effective_zap' observation for player1 should be False"
    assert scene_description['player2']['effective_zap'] == False, "The 'effective_zap' observation for player2 should be False"
    assert scene_description['player3']['effective_zap'] == False, "The 'effective_zap' observation for player3 should be False"