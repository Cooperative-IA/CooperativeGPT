# Copyright 2022 DeepMind Technologies Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Configuration for running a Coins game in Melting Pot.

Example video: https://youtu.be/a_SYgt4tBsc
"""

from collections.abc import Mapping, Sequence
import random
from typing import Any, Dict

from meltingpot.utils.substrates import colors
from meltingpot.utils.substrates import game_object_utils
from meltingpot.utils.substrates import shapes
from meltingpot.utils.substrates import specs
from ml_collections import config_dict as configdict

PrefabConfig = game_object_utils.PrefabConfig

# Warning: setting `_ENABLE_DEBUG_OBSERVATIONS = True` may cause slowdown.
_ENABLE_DEBUG_OBSERVATIONS = False

MANDATED_NUM_PLAYERS = 2  # TODO

COIN_PALETTES = {
    "coin_red": shapes.get_palette((238, 102, 119)),    # Red.
    #"coin_blue": shapes.get_palette((68, 119, 170)),    # Blue.
    "coin_yellow": shapes.get_palette((204, 187, 68)),  # Yellow.
    #"coin_green": shapes.get_palette((34, 136, 51)),    # Green.
    #"coin_purple": shapes.get_palette((170, 51, 119))   # Purple.
}

FLOOR = {
    "name": "floor",
    "components": [
        {
            "component": "StateManager",
            "kwargs": {
                "initialState": "floor",
                "stateConfigs": [{
                    "state": "floor",
                    "layer": "background",
                    "sprite": "Floor",
                }],
            }
        },
        {"component": "Transform",},
        {
            "component": "Appearance",
            "kwargs": {
                "renderMode": "ascii_shape",
                "spriteNames": ["Floor"],
                "spriteShapes": [shapes.GRAINY_FLOOR],
                "palettes": [{"*": (0, 0, 0, 255),
                              "+": (30, 30, 30, 255),}],
                "noRotates": [False]
            }
        },
    ]
}

def get_ascii_map(
    min_width: int, max_width: int, min_height: int, max_height: int) -> str:
  """Procedurally generate ASCII map."""
  assert min_width <= max_width
  assert min_height <= max_height

  # Sample random map width and height.
  width = random.randint(min_width, max_width)
  height = random.randint(min_height, max_height)

  # Make top row (walls). Pad to max width to ensure all maps are same size.
  ascii_map = ["W"] * (width + 2) + [" "] * (max_width - width)

  # Make middle rows (navigable interior).
  for row in range(height):
    # Add walls and coins.
    ascii_map += ["\nW"] + ["C"] * width + ["W"]

    if row == 1:
      # Add top-right spawn point.
      ascii_map[-3] = "_"
    elif row == height - 2:
      # Add bottom-left spawn point.
      ascii_map[-width] = "_"

    # Pad to max width.
    ascii_map += [" "] * (max_width - width)

  # Make bottom row (walls). Pad to max width.
  ascii_map += ["\n"] + ["W"] * (width + 2) + [" "] * (max_width - width)

  # Pad with extra rows to reach max height.
  for _ in range(max_height - height):
    ascii_map += ["\n"] + [" "] * max_width

  # Join list of strings into single string.
  ascii_map = "".join(ascii_map)

  # Append \n at the beginning and at the end of the string
  ascii_map = "\n" + ascii_map + "\n"

  return ascii_map

# `prefab` determines which prefab game object to use for each `char` in the
# ascii map.
CHAR_PREFAB_MAP = {
    "_": {"type": "all", "list": ["floor", "spawn_point"]},
    "W": "wall",
    "C": {"type": "all", "list": ["floor", "coin"]},
    
}

_COMPASS = ["N", "E", "S", "W"]


# The Scene objece is a non-physical object, it components implement global
# logic. In this case, that includes holding the global berry counters to
# implement the regrowth rate, as well as some of the observations.
SCENE = {
    "name": "scene",
    "components": [
        {
            "component": "StateManager",
            "kwargs": {
                "initialState": "scene",
                "stateConfigs": [{
                    "state": "scene",
                }],
            }
        },
        {
            "component": "Transform",
        },
        {
            "component": "GlobalCoinCollectionTracker",
            "kwargs": {
                "numPlayers": MANDATED_NUM_PLAYERS,
            },
        },
        {
              "component": "AvatarsStateObserver",
              "kwargs": {}
        },
        {
            "component": "GlobalStateTracker",
            "kwargs": {
                "numPlayers": MANDATED_NUM_PLAYERS,
            },
            
        },     
                  {
              "component": "GlobalMetricHolder",
              "kwargs": {
                  "metrics": [
                      {"type": "tensor.Int32Tensor",
                       "shape": (MANDATED_NUM_PLAYERS, MANDATED_NUM_PLAYERS),
                       "variable": "playerZapMatrix"},
                  ]
              }
          },
           {
              "component": "GlobalMetricReporter",
              "kwargs": {
                  "metrics": [
                      {"name": "WHO_ZAPPED_WHO",
                       "type": "tensor.Int32Tensor",
                       "shape": (MANDATED_NUM_PLAYERS, MANDATED_NUM_PLAYERS),
                       "component": "GlobalMetricHolder",
                       "variable": "playerZapMatrix"},
                      {"name": "AVATAR_STATES",
                       "type": "tensor.Int32Tensor",
                       "shape": (MANDATED_NUM_PLAYERS,),
                       "component": "GlobalStateTracker",
                       "variable": "states"}
                  ]
              }
          },
        {
            "component": "StochasticIntervalEpisodeEnding",
            "kwargs": {
                "minimumFramesPerEpisode": 3000000,
                "intervalLength": 1000000,  # Set equal to unroll length.
                "probabilityTerminationPerInterval": 0.001
            }
        }
    ]
}
if _ENABLE_DEBUG_OBSERVATIONS:
  SCENE["components"].append({
      "component": "GlobalMetricReporter",
      "kwargs": {
          "metrics": [
              {
                  "name": "COINS_COLLECTED",
                  "type": "tensor.Int32Tensor",
                  "shape": (MANDATED_NUM_PLAYERS, 2),
                  "component": "GlobalCoinCollectionTracker",
                  "variable": "coinsCollected",
              },
          ]
      },
  })


WALL = {
    "name": "wall",
    "components": [
        {
            "component": "StateManager",
            "kwargs": {
                "initialState": "wall",
                "stateConfigs": [{
                    "state": "wall",
                    "layer": "upperPhysical",
                    "sprite": "Wall",
                }],
            }
        },
        {"component": "Transform",},
        {
            "component": "Appearance",
            "kwargs": {
                "renderMode": "ascii_shape",
                "spriteNames": ["Wall",],
                "spriteShapes": [shapes.WALL],
                "palettes": [{"*": (95, 95, 95, 255),
                              "&": (100, 100, 100, 255),
                              "@": (109, 109, 109, 255),
                              "#": (152, 152, 152, 255)}],
                "noRotates": [True]
            }
        },
        {
            "component": "BeamBlocker",
            "kwargs": {
                "beamType": "gift"
            }
        },
        {
            "component": "BeamBlocker",
            "kwargs": {
                "beamType": "zap"
            }
        },
    ]
}

SPAWN_POINT = {
    "name": "spawnPoint",
    "components": [
        {
            "component": "StateManager",
            "kwargs": {
                "initialState": "spawnPoint",
                "stateConfigs": [{
                    "state": "spawnPoint",
                    "layer": "logic",
                    "groups": ["spawnPoints"]
                }],
            }
        },
        {"component": "Transform",},
    ]
}


def get_coin(
    coin_type_a: str,
    coin_type_b: str,
    regrow_rate: float,
    reward_self_for_match: float,
    reward_self_for_mismatch: float,
    reward_other_for_match: float,
    reward_other_for_mismatch: float,
    ) -> PrefabConfig:
  """Create `PrefabConfig` for coin component."""
  return {
      "name": "coin",
      "components": [
          {
              "component": "StateManager",
              "kwargs": {
                  "initialState": "coinWait",
                  "stateConfigs": [
                      {"state": coin_type_a,
                       "layer": "superOverlay",
                       "sprite": coin_type_a,
                      },
                      {"state": coin_type_b,
                       "layer": "superOverlay",
                       "sprite": coin_type_b,
                      },
                      {"state": "coinWait",
                       "layer": "logic",
                      },
                  ]
              }
          },
          {"component": "Transform",},
          {
              "component": "Appearance",
              "kwargs": {
                  "renderMode": "ascii_shape",
                  "spriteNames": [coin_type_a, coin_type_b],
                  "spriteShapes": [shapes.COIN] * 2,
                  "palettes": [COIN_PALETTES[coin_type_a],
                               COIN_PALETTES[coin_type_b]],
                  "noRotates": [False] * 2,
              }
          },
          {
              "component": "Coin",
              "kwargs": {
                  "waitState": "coinWait",
                  "rewardSelfForMatch": reward_self_for_match,
                  "rewardSelfForMismatch": reward_self_for_mismatch,
                  "rewardOtherForMatch": reward_other_for_match,
                  "rewardOtherForMismatch": reward_other_for_mismatch,
              }
          },
          {
              "component": "ChoiceCoinRegrow",
              "kwargs": {
                  "liveStateA": coin_type_a,
                  "liveStateB": coin_type_b,
                  "waitState": "coinWait",
                  "regrowRate": regrow_rate,
              }
          },
      ]
  }


human_readable_colors = list(colors.human_readable)
TARGET_SPRITE_SELF = {
    "name": "Self",
    "shape": shapes.CUTE_AVATAR,
    "palette": shapes.get_palette(human_readable_colors.pop(0)),
    "noRotate": True,
}
def get_avatar(coin_type: str, 
               player_idx: int,
               target_sprite_self: Dict[str, Any],
               palete_type: Dict[str, Any],
               ) -> Dict[str, Any]:
  """Create an avatar object."""
  
    # Lua is 1-indexed.
  lua_index = player_idx + 1

  # Setup the self vs other sprite mapping.
  source_sprite_self = "Avatar" + str(lua_index)
  custom_sprite_map = {source_sprite_self: target_sprite_self["name"]}

  live_state_name = "player{}".format(lua_index)
  avatar_object = {
      "name": "avatar",
      "components": [
          {
              "component": "StateManager",
              "kwargs": {
                  "initialState": live_state_name,
                  "stateConfigs": [
                      {"state": live_state_name,
                       "layer": "upperPhysical",
                       "sprite": source_sprite_self,
                       "contact": "avatar",
                       "groups": ["players"]},

                      {"state": "playerWait",
                       "groups": ["playerWaits"]},
                  ]
              }
          },
          {
              "component": "Transform",
          },
          {
              "component": "Appearance",
              "kwargs": {
                  "renderMode": "ascii_shape",
                  "spriteNames": [source_sprite_self],
                  "spriteShapes": [shapes.CUTE_AVATAR],
                  # Palette to be overwritten.
                  "palettes": [palete_type],
                  "noRotates": [True]
              }
          },
          {
              "component": "Avatar",
              "kwargs": {
                  "index": lua_index,  # Player index to be overwritten.
                  "aliveState": live_state_name,
                  "waitState": "playerWait",
                  "spawnGroup": "spawnPoints",
                  "actionOrder": ["move", 
                                  "turn",
                                  "fireZap"],
                  "actionSpec": {
                      "move": {"default": 0, "min": 0, "max": len(_COMPASS)},
                      "turn": {"default": 0, "min": -1, "max": 1},
                      "fireZap": {"default": 0, "min": 0, "max": 1},
                  },
                  "view": {
                      "left": 5,
                      "right": 5,
                      "forward": 9,
                      "backward": 1,
                      "centered": False
                  }
              }
          },
          {
              "component": "AvatarIdsInViewObservation"
          },
          {
              "component": "Zapper",
              "kwargs": {
                  "cooldownTime": 10,
                  "beamLength": 3,
                  "beamRadius": 1,
                  "framesTillRespawn": 50,
                  "penaltyForBeingZapped": 0,
                  "rewardForZapping": 0,
                  "removeHitPlayer": True,
              }
          },
          {
              "component": "ReadyToShootObservation",
          },
          {
              "component": "LocationObserver",
              "kwargs": {"objectIsAvatar": True, "alsoReportOrientation": True},
          },
          {
              "component": "PlayerCoinType",
              "kwargs": {
                  "coinType": coin_type,
              },
          },
          {
              "component": "Role",
              "kwargs": {
                  #  Role has no effect if all factors are 1.0.
                  "multiplyRewardSelfForMatch": 1.0,
                  "multiplyRewardSelfForMismatch": 1.0,
                  "multiplyRewardOtherForMatch": 1.0,
                  "multiplyRewardOtherForMismatch": 1.0,
              },
          },
          {
              "component": "PartnerTracker",
          },
      ]
  }
  # Signals needed for puppeteers.
  metrics = [
      {
          "name": "MISMATCHED_COIN_COLLECTED_BY_PARTNER",
          "type": "Doubles",
          "shape": [],
          "component": "PartnerTracker",
          "variable": "partnerCollectedMismatch",
      },
  ]
  if True:
    avatar_object["components"].append({
        "component": "LocationObserver",
        "kwargs": {"objectIsAvatar": True, "alsoReportOrientation": True},
    })
    # Debug metrics
    metrics.append({
        "name": "MATCHED_COIN_COLLECTED",
        "type": "Doubles",
        "shape": [],
        "component": "Role",
        "variable": "cumulantCollectedMatch",
    })
    metrics.append({
        "name": "MISMATCHED_COIN_COLLECTED",
        "type": "Doubles",
        "shape": [],
        "component": "Role",
        "variable": "cumulantCollectedMismatch",
    })
    metrics.append({
        "name": "MATCHED_COIN_COLLECTED_BY_PARTNER",
        "type": "Doubles",
        "shape": [],
        "component": "PartnerTracker",
        "variable": "partnerCollectedMatch",
    })

  # Add the metrics reporter.
  avatar_object["components"].append({
      "component": "AvatarMetricReporter",
      "kwargs": {"metrics": metrics}
  })

  return avatar_object

# `prefabs` is a dictionary mapping names to template game objects that can
# be cloned and placed in multiple locations accoring to an ascii map.
def get_prefabs(
    coin_type_a: str,
    coin_type_b: str,
    regrow_rate: float = 0.0005,
    reward_self_for_match: float = 1.0,
    reward_self_for_mismatch: float = 1.0,
    reward_other_for_match: float = 0.0,
    reward_other_for_mismatch: float = -2.0,
) -> PrefabConfig:
  """Make `prefabs` (a dictionary mapping names to template game objects)."""
  coin = get_coin(coin_type_a=coin_type_a,
                  coin_type_b=coin_type_b,
                  regrow_rate=regrow_rate,
                  reward_self_for_match=reward_self_for_match,
                  reward_self_for_mismatch=reward_self_for_mismatch,
                  reward_other_for_match=reward_other_for_match,
                  reward_other_for_mismatch=reward_other_for_mismatch)
  return {"wall": WALL, "spawn_point": SPAWN_POINT, "coin": coin, "floor": FLOOR}


# `player_color_palettes` is a list with each entry specifying the color to use
# for the player at the corresponding index.
# These correspond to the persistent agent colors, but are meaningless for the
# human player. They will be overridden by the environment_builder.
def get_player_color_palettes(
    coin_type_a: str, coin_type_b: str) -> Sequence[Mapping[str, shapes.Color]]:
  return [COIN_PALETTES[coin_type_a], COIN_PALETTES[coin_type_b]]

# Primitive action components.
# pylint: disable=bad-whitespace
# pyformat: disable
NOOP       = {"move": 0, "turn":  0, "fireZap": 0}
FORWARD    = {"move": 1, "turn":  0, "fireZap": 0}
STEP_RIGHT = {"move": 2, "turn":  0, "fireZap": 0}
BACKWARD   = {"move": 3, "turn":  0, "fireZap": 0}
STEP_LEFT  = {"move": 4, "turn":  0, "fireZap": 0}
TURN_LEFT  = {"move": 0, "turn": -1, "fireZap": 0}
TURN_RIGHT = {"move": 0, "turn":  1, "fireZap": 0}
FIRE_ZAP   = {"move": 0, "turn":  0, "fireZap": 1}
# pyformat: enable
# pylint: enable=bad-whitespace

ACTION_SET = (
    NOOP,
    FORWARD,
    BACKWARD,
    STEP_LEFT,
    STEP_RIGHT,
    TURN_LEFT,
    TURN_RIGHT,
    FIRE_ZAP,
)


def get_config(players:list[str]):
  """Default configuration for the Coins substrate."""
  
  
  # Error if the player list is empty.
  if not players:
    raise ValueError("Must specify at least one player.")   


  config = configdict.ConfigDict()

  # Set the size of the map.
  config.min_width = 15
  config.max_width = 15
  config.min_height = 15
  config.max_height = 15

  # Action set configuration.
  config.action_set = ACTION_SET


  # Observation format configuration.
  config.individual_observation_names = [
      "RGB",
      # Global switching signals for puppeteers.
      "MISMATCHED_COIN_COLLECTED_BY_PARTNER",
  ]
  config.global_observation_names = [
      "WORLD.RGB"
  ]

  # The specs of the environment (from a single-agent perspective).
  config.action_spec = specs.action(len(ACTION_SET))
  config.timestep_spec = specs.timestep({
      "RGB": specs.OBSERVATION["RGB"],
      # Switching signals for puppeteers.
      "MISMATCHED_COIN_COLLECTED_BY_PARTNER": specs.float64(),
      # Debug only (do not use the following observations in policies).
      "WORLD.RGB": specs.rgb(136, 136),
  })
  # The roles assigned to each player.
  config.valid_roles = frozenset({"default"})
  config.default_player_roles = ("default",) * MANDATED_NUM_PLAYERS
  config.num_players = len(players)
  config.player_names = players

  return config




def create_avatar_objects(num_players, coin_types, paletes):
  """Returns list of avatar objects of length 'num_players'."""
  avatar_objects = []
  for player_idx in range(0, num_players):
    coin_type = coin_types[player_idx%len(coin_types)]
    palete_type = paletes[player_idx%len(coin_types)]
    game_object =  get_avatar(coin_type=coin_type, player_idx=player_idx, target_sprite_self=TARGET_SPRITE_SELF, palete_type=palete_type)
    avatar_objects.append(game_object)
  
  return avatar_objects


config = get_config([""]*MANDATED_NUM_PLAYERS)
ASCII_MAP = get_ascii_map(min_width=config.min_width,
                               max_width=config.max_width,
                               min_height=config.min_height,
                               max_height=config.max_height)    
def build(
    config: configdict.ConfigDict,
) -> Mapping[str, Any]:
  """Build the coins substrate given player roles."""
  #assert len(roles) == MANDATED_NUM_PLAYERS, "Wrong number of players"
  ### Randomly choose colors.
  #coin_type_a, coin_type_b = random.sample(tuple(COIN_PALETTES), k=2)
  #Select coin_type_a as the yellow coin and coin_type_b as the red coin
  coin_type_a, coin_type_b =  "coin_yellow", "coin_red"
  # Manually build avatar config.
  num_players = MANDATED_NUM_PLAYERS
  player_color_palettes = get_player_color_palettes(
      coin_type_a=coin_type_a, coin_type_b=coin_type_b)
  
  avatar_objects = create_avatar_objects(MANDATED_NUM_PLAYERS, [coin_type_a, coin_type_b], player_color_palettes)
  #avatar_objects = game_object_utils.build_avatar_objects(
  #    num_players, {"avatar": created_avatars}, player_color_palettes)  # pytype: disable=wrong-arg-types  # allow-recursive-types
  #game_object_utils.get_first_named_component(
  #    avatar_objects[1], "PlayerCoinType")["kwargs"]["coinType"] = coin_type_b

  # Build the substrate definition.
  substrate_definition = dict(
      levelName="coins_original",
      levelDirectory="meltingpot/lua/levels",
      numPlayers=num_players,
      # Define upper bound of episode length since episodes end stochastically.
      maxEpisodeLengthFrames=5000,
      spriteSize=8,
      topology="BOUNDED",  # Choose from ["BOUNDED", "TORUS"],
      simulation={
          "map": get_ascii_map(min_width=config.min_width,
                               max_width=config.max_width,
                               min_height=config.min_height,
                               max_height=config.max_height),
          "scene": SCENE,
          "prefabs": get_prefabs(coin_type_a=coin_type_a,
                                 coin_type_b=coin_type_b),
          "charPrefabMap": CHAR_PREFAB_MAP,
          "gameObjects": avatar_objects,
      }
  )
  return substrate_definition
