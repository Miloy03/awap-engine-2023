from src.game_constants import RobotType, Direction, Team, TileState
from src.game_state import GameState, GameInfo
from src.player import Player
from src.map import TileInfo, RobotInfo
import random
from typing import List


class BotPlayer(Player):
    """
    Players will write a child class that implements (notably the play_turn method)
    """
    list_of_spawned_places = []

    def __init__(self, team: Team):
        self.team = team
        return

    def find_unoccupied_ally_tiles(self, game_info: GameInfo) -> List[TileInfo]:
        ally_tiles = []
        for row in range(len(game_info.map)):
            for col in range(len(game_info.map[0])):
                # get the tile at (row, col)
                tile = game_info.map[row][col]
                # skip fogged tiles
                if tile is not None:  # ignore fogged tiles
                    if tile.robot is None:  # ignore occupied tiles
                        if tile.terraform > 0:  # ensure tile is ally-terraformed
                            ally_tiles += [tile]
        return ally_tiles

    def play_turn(self, game_state: GameState) -> None:


        # get info
        ginfo = game_state.get_info()

        # get turn/team info
        height, width = len(ginfo.map), len(ginfo.map[0])

        # print info about the game
        print(f"Turn {ginfo.turn}, team {ginfo.team}")
        print("Map height", height)
        print("Map width", width)

        # spawn on a random tile
        print(f"My metal {game_state.get_metal()}")

        robots = game_state.get_ally_robots()

        # Count the number of robots of each type
        num_explorers = 0
        num_terraformers = 0
        num_miners = 0

        for robot in robots.values():
            if robot.type == RobotType.EXPLORER:
                num_explorers += 1
            elif robot.type == RobotType.TERRAFORMER:
                num_terraformers += 1
            elif robot.type == RobotType.MINER:
                num_miners += 1

        total_robots = num_explorers + num_terraformers + num_miners

        # print("Number of Explorers: ", num_explorers)
        # print("Number of Terra: " , num_terraformers)
        # print("Number of Miners: " , num_miners)

        # base case 1
        if total_robots == 0:
            spawn_types = [RobotType.EXPLORER]
        if game_state.get_metal() == 200:
            spawn_types = [RobotType.EXPLORER]
        elif num_explorers / total_robots < 0.4:
            spawn_types = [RobotType.EXPLORER]
        elif num_terraformers / total_robots < 0.5:
            spawn_types = [RobotType.TERRAFORMER]
        elif num_miners / total_robots < 0.10:
            spawn_types = [RobotType.MINER]
        else:
            spawn_types = []

        spawned_robots = []
        # find un-occupied ally tile
        for spawn_type in spawn_types:
            spawned_occupied_tiles = []
            ally_tiles = self.find_unoccupied_ally_tiles(ginfo)
            for x in spawned_occupied_tiles:
                ally_tiles.remove(x)
            if len(self.list_of_spawned_places) > 2:
                for x in self.list_of_spawned_places:
                    if x in ally_tiles:
                        ally_tiles.remove(x)
            print("Ally tiles", ally_tiles)
            if len(ally_tiles) > 0:
                # pick a random one to spawn on
                spawn_loc = random.choice(ally_tiles)
                # spawn the robot
                # print(f"Spawning robot at {spawn_loc.row, spawn_loc.col}")
                # print(f"Spawning robot type: {spawn_type}")
                # check if we can spawn here (checks if we can afford, tile is empty, and tile is ours)
                if game_state.can_spawn_robot(spawn_type, spawn_loc.row, spawn_loc.col):
                    spawned_robots += [game_state.spawn_robot(spawn_type, spawn_loc.row, spawn_loc.col)]
                    # print("Spawned Robot", spawned_robots[-1])
                spawned_occupied_tiles += [spawn_loc]
                self.list_of_spawned_places += [spawn_loc]

        # move robots
        robots = game_state.get_ally_robots()

        # iterate through dictionary of robots
        for rname, rob in robots.items():
            # print(f"Robot {rname} at {rob.row, rob.col}")

            # randomly move if possible
            all_dirs = [dir for dir in Direction]
            move_dir = random.choice(all_dirs)

            # check if we can move in this direction
            if game_state.can_move_robot(rname, move_dir):
                # try to not collide into robots from our team
                dest_loc = (rob.row + move_dir.value[0], rob.col + move_dir.value[1])
                dest_tile = game_state.get_map()[dest_loc[0]][dest_loc[1]]

                if dest_tile.robot is None or dest_tile.robot.team != self.team:
                    game_state.move_robot(rname, move_dir)

            # action if possible
            if game_state.can_robot_action(rname):
                game_state.robot_action(rname)
                # if dest_tile.state == "TileState.TERRAFORMABLE":
                #     print("Something nice")
                # print(dest_tile, "Miner")
                # print(rname.type, "Printed Type")

