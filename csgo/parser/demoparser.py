import logging
import os
import subprocess
import pandas as pd

from csgo.events import Round, Kill, Damage, Grenade, Flashed, PlayerInfo, BombEvent, ItemPickup
from csgo.utils import NpEncoder, check_go_version

class DemoParser:
    """ This class can parse a CSGO demofile to output game data in a logical structure. Accessible via csgo.parser import DemoParser

    Attributes:
        demofile (string) : A string denoting the path to the demo file, which ends in .dem
        log (boolean)     : A boolean denoting if a log will be written. If true, log is written to "csgo_parser.log"
        match_id (string) : A unique demo name/game id
    
    Raises:
        ValueError : Raises a ValueError if the Golang version is lower than 1.14
    """

    def __init__(
        self, demofile="", log=False, match_id="",
    ):
        self.demofile = demofile
        self.rounds = []
        self.demo_error = False
        if match_id == "":
            self.match_id = demofile[demofile.rfind("/") + 1 : -4]
        else:
            self.match_id = match_id
        acceptable_go = check_go_version()
        if log:
            logging.basicConfig(
                filename="csgo_parser.log",
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%H:%M:%S",
            )
            self.logger = logging.getLogger("CSGODemoParser")
            self.logger.handlers = []
            fh = logging.FileHandler("csgo_parser.log")
            fh.setLevel(logging.INFO)
            self.logger.addHandler(fh)
            self.logger.info(
                "Initialized CSGODemoParser with demofile " + self.demofile
            )
            if not acceptable_go:
                self.logger.error("Go version too low! Needs 1.14.0")
                raise ValueError("Go version too low! Needs 1.14.0")
            else:
                self.logger.info("Go version>=1.14.0")
        else:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%H:%M:%S",
            )
            self.logger = logging.getLogger("CSGODemoParser")
            self.logger.info(
                "Initialized CSGODemoParser with demofile " + self.demofile
            )
            if not acceptable_go:
                self.logger.error("Go version too low! Needs 1.14.0")
                raise ValueError("Go version too low! Needs 1.14.0")
            else:
                self.logger.info("Go version>=1.14.0")

    @staticmethod
    def get_seconds(start_tick, tick):
        """ Finds seconds since start of round

        Args:
            start_tick (int) : Round start tick
            tick (int)       : Tick of event
        """
        return (tick - start_tick) / 128

    @staticmethod
    def get_round_type(ct_equip, t_equip, round_num):
        """ Return team round types for a given dollar amount

        Args:
            ct_equip (int)  : CT side equipment value
            t_equip (int)   : T side equipment value
            round_num (int) : Round number
        """
        round_types = {"CT": "None", "T": "None"}
        # Pistol Round
        if (round_num == 1) or (round_num == 16):
            round_types["CT"] = "Pistol"
            round_types["T"] = "Pistol"
            return round_types
        # Full Eco
        if ct_equip < 2000:
            round_types["CT"] = "Full Eco"
        if t_equip < 2000:
            round_types["CT"] = "Full Eco"
        # Eco
        if (ct_equip >= 2000) and (ct_equip < 8500):
            round_types["CT"] = "Eco"
        if (t_equip >= 2000) and (t_equip < 8500):
            round_types["T"] = "Eco"
        # Anti-Eco
        if (
            (round_types["T"] == "Eco" or round_types["T"] == "Full Eco")
            and (ct_equip < 18500)
            and (ct_equip >= 8500)
        ):
            round_types["CT"] = "Anti-Eco"
        if (
            (round_types["CT"] == "Eco" or round_types["CT"] == "Full Eco")
            and (t_equip < 18500)
            and (t_equip >= 8500)
        ):
            round_types["T"] = "Anti-Eco"
        # Half Buy
        if (ct_equip >= 8500) and (ct_equip < 22000):
            round_types["CT"] = "Half Buy"
        if (t_equip >= 8500) and (t_equip < 20000):
            round_types["T"] = "Half Buy"
        # Full Buy
        if ct_equip >= 22000:
            round_types["CT"] = "Full Buy"
        if t_equip > 20000:
            round_types["T"] = "Full Buy"
        return round_types

    @staticmethod
    def get_hit_group(hitgroup_id):
        """ Return hitgroup in string. The mapping is:

        Args:
            hitgroup_id (int) : Hitgroup identifier

        Returns:
            String corresponding to the hitgroup id
        """
        hit_groups = {
            1: "Generic",
            2: "Head",
            3: "Chest",
            4: "Stomach",
            5: "LeftArm",
            6: "RightArm",
            7: "LeftLeg",
            8: "RightLeg",
            9: "Gear",
        }
        return hit_groups.get(hitgroup_id, "NA")

    @staticmethod
    def get_weapon(weapon_id):
        """ Return weapon name given a weapon_id. The mapping is:

        Args:
            weapon_id (int) : Weapon identifier

        returns:
            String corresponding to the weapon id
        """
        weapon_ids = {
            0: "Unknown",
            1: "P2000",
            2: "Glock",
            3: "P250",
            4: "Deagle",
            5: "FiveSeven",
            6: "DualBerettas",
            7: "Tec9",
            8: "CZ",
            9: "USP",
            10: "Revolver",
            101: "MP7",
            102: "MP9",
            103: "Bizon",
            104: "Mac10",
            105: "UMP",
            106: "P90",
            107: "MP5",
            201: "SawedOff",
            202: "Nova",
            203: "Swag7",
            204: "XM1014",
            205: "M249",
            206: "Negev",
            301: "Galil",
            302: "Famas",
            303: "AK47",
            304: "M4A4",
            305: "M4A1",
            306: "Scout",
            307: "SG556",
            308: "AUG",
            309: "AWP",
            310: "Scar20",
            311: "G3SG1",
            401: "Zeus",
            402: "Kevlar",
            403: "Helmet",
            404: "Bomb",
            405: "Knife",
            406: "DefuseKit",
            407: "World",
            501: "Decoy",
            502: "Molotov",
            503: "Incendiary",
            504: "Flash",
            505: "Smoke",
            506: "HE",
        }
        return weapon_ids.get(weapon_id, "NA")

    @staticmethod
    def get_round_reason(reason_id):
        """ Return round reason name. The mapping is:

        Args:
            reason_id (int) : Round reason identifier

        Returns:
            String corresponding to the round win reason
        """
        round_reasons = {
            1: "TargetBombed",
            7: "BombDefused",
            8: "CTWin",
            9: "TerroristsWin",
            10: "Draw",
            12: "TargetSaved",
        }
        return round_reasons.get(reason_id, "NA")

    def _parse_demofile(self):
        """ Parse a demofile using the Go script parse_demofile.go -- this function takes no arguments

        Returns:
            Returns a list of strings to the "parsed_text" attribute of the DemoParser class.
        """
        self.logger.info(
            "Starting CSGO Golang demofile parser, reading in "
            + os.getcwd()
            + "/"
            + self.demofile
        )
        path = os.path.join(os.path.dirname(__file__), "")
        self.logger.info("Running Golang parser from " + path)
        proc = subprocess.Popen(
            [
                "go",
                "run",
                "parse_demofile.go",
                "-demo",
                os.getcwd() + "/" + self.demofile,
            ],
            stdout=subprocess.PIPE,
            cwd=path,
        )
        self.parsed_text = proc.stdout.read().splitlines()
        proc.kill()
        self.parsed_text = [event.decode("utf-8") for event in self.parsed_text]
        self.parsed_text = [event[:-1] for event in self.parsed_text]
        if "[ERROR]" in self.parsed_text[0]:
            self.demo_error = True
        self.logger.info("Demofile parsing complete")

    def _parse_match(self):
        """ Parse match event text data and structure it in logical format.
        """
        self.logger.info("Parsing match events")
        self.rounds = []
        
        # Set default round stuff
        current_round = Round()
        current_damages_list = []
        current_kills_list = []
        current_enemiesflash_list = []
        current_teamflash_list = []     
        current_grenade_list = []
        current_playerInfo_list = []  
        current_bomb_events_list = []
        current_itemPickup_list = []
        
        
        current_round.start_tick = 0
        
        for event in self.parsed_text:
            if "[MATCH START]" in event:
                current_round = Round()
                current_damages_list = []
                current_kills_list = []
                current_enemiesflash_list = []
                current_teamflash_list = []      
                current_grenade_list = []
                current_playerInfo_list = []  
                current_bomb_events_list = []         
                current_itemPickup_list = []
                parsed_line = event.split("] [")[1].replace("]", "").split(",")
                current_round.map_name = parsed_line[0]
                current_round.start_tick = int(parsed_line[1].strip())
                self.logger.info("Parsed match start " + str(len(self.rounds)))
            if "[ROUND START]" in event:
                current_round = Round()
                current_damages_list = []
                current_kills_list = []
                current_enemiesflash_list = []
                current_teamflash_list = []            
                current_grenade_list = []
                current_playerInfo_list = []       
                current_bomb_events_list = []   
                current_itemPickup_list = []
                # First block
                split_line = event.split("] [")
                first_block = split_line[1].split(",")
                current_round.map_name = first_block[0]
                current_round.start_tick = int(first_block[1].strip())
                # Second block
                second_block = split_line[2].replace("]", "").split(",")
                current_round.start_t_score = int(second_block[0])
                current_round.start_ct_score = int(second_block[1].strip())
                self.logger.info("Parsed round start " + str(len(self.rounds)))
            if "[ROUND END]" in event and "DRAW" not in event:
                split_line = event.split("] [")
                # First block
                first_block = split_line[1].split(",")
                current_round.map_name = first_block[0]
                current_round.end_tick = int(first_block[1].strip())
                # Second block
                second_block = split_line[2].split(",")
                current_round.end_t_score = int(second_block[0])
                current_round.end_ct_score = int(second_block[1].strip())
                # Third block
                third_block = split_line[3].replace("]", "").split(",")
                current_round.round_winner_side = third_block[0]
                current_round.round_winner = third_block[1].strip()
                current_round.round_loser = third_block[2].strip()
                current_round.reason = DemoParser.get_round_reason(
                    int(third_block[3].strip())
                )
                # Add events to round
                current_round.kills = current_kills_list
                current_round.damages = current_damages_list
                current_round.grenades = current_grenade_list
                current_round.current_enemiesflash = current_enemiesflash_list
                current_round.current_teamflash = current_teamflash_list
                current_round.current_playerInfo= current_playerInfo_list              
                current_round.bomb_events = current_bomb_events_list
                current_round.current_itemPickup = current_itemPickup_list
        
                # Add round to list
                self.rounds.append(current_round)
                self.logger.info("Parsed round end " + str(len(self.rounds)))
            if "[ROUND PURCHASE]" in event:
                split_line = event.split("] [")
                # First block
                first_block = split_line[1].split(",")
                current_round.map_name = first_block[0]
                # Second block
                second_block = split_line[2].split(",")
                current_round.t_cash_spent_total = int(second_block[1])
                current_round.t_cash_spent_round = int(second_block[2])
                current_round.t_eq_val = int(second_block[3])
                # Third block
                third_block = split_line[3].replace("]", "").split(",")
                current_round.ct_cash_spent_total = int(third_block[1])
                current_round.ct_cash_spent_round = int(third_block[2])
                current_round.ct_eq_val = int(third_block[3])
                round_types = DemoParser.get_round_type(
                    current_round.ct_eq_val,
                    current_round.t_eq_val,
                    len(self.rounds) + 1,
                )
                current_round.ct_round_type = round_types["CT"]
                current_round.t_round_type = round_types["T"]
            if "[ROUND END OFFICIAL]" in event:
                split_line = event.split("] [")
                # First block
                first_block = split_line[1].split(",")
                current_round.map_name = first_block[0]
                current_round.end_tick = int(first_block[1].replace("]", "").strip())
                # Add events to round
                current_round.kills = current_kills_list
                current_round.damages = current_damages_list
                current_round.grenades = current_grenade_list
                current_round.current_enemiesflash = current_enemiesflash_list
                current_round.current_teamflash = current_teamflash_list
                current_round.current_playerInfo = current_playerInfo_list            
                current_round.bomb_events = current_bomb_events_list
                current_round.current_itemPickup = current_itemPickup_list
                # Add round to list
                if len(self.rounds) > 0:
                    self.rounds[-1] = current_round
                self.logger.info("Parsed round end official " + str(len(self.rounds)))
            
            if "[FREEZE END]" in event:
                split_line = event.split("] [")
                # First block
                first_block = split_line[1].split(",")
                current_round.end_freezetime = int(first_block[0].replace("]", "").strip())
   
            if "[DAMAGE]" in event:
                current_damage = Damage()
                split_line = event.split("] [")
                # First block
                current_damage.tick = int(split_line[1].split(",")[1].strip())
                current_damage.sec = DemoParser.get_seconds(
                    current_round.start_tick, current_damage.tick
                )
                # Second block
                second_block = split_line[2].split(",")
                current_damage.victim_x_viz = float(second_block[0])
                current_damage.victim_y_viz = float(second_block[1].strip())
                current_damage.victim_view_x = float(second_block[2].strip())
                current_damage.victim_view_y = float(second_block[3].strip())
                current_damage.victim_area_name = second_block[4].strip()
                # Third block
                third_block = split_line[3].split(",")
                current_damage.attacker_x_viz = float(third_block[0])
                current_damage.attacker_y_viz = float(third_block[1].strip())
                current_damage.attacker_view_x = float(third_block[2].strip())
                current_damage.attacker_view_y = float(third_block[3].strip())
                current_damage.attacker_area_name = third_block[4].strip()
                # Fourth block
                fourth_block = split_line[4].split(",")
                current_damage.victim_id = int(fourth_block[0])
                current_damage.victim_name = fourth_block[1].strip()
                current_damage.victim_side = fourth_block[2].strip()
                # Fifth block
                fifth_block = split_line[5].split(",")
                current_damage.attacker_id = int(fifth_block[0])
                current_damage.attacker_name = fifth_block[1].strip()
                current_damage.attacker_side = fifth_block[2].strip()
                # Sixth block
                sixth_block = split_line[6].split(",")
                current_damage.hp_damage = int(sixth_block[0])
                current_damage.kill_hp_damage = int(sixth_block[1])
                current_damage.armor_damage = int(sixth_block[2].strip())
                current_damage.weapon_id = DemoParser.get_weapon(
                    int(sixth_block[3].strip())
                )
                current_damage.hit_group = DemoParser.get_hit_group(
                    int(sixth_block[4].replace("]", "").strip())
                )
                # Add current damage to round
                current_damages_list.append(current_damage)
                
            if "[KILL]" in event:
                current_kill = Kill()
                split_line = event.split("] [")
                # First block
                current_kill.tick = int(split_line[1])
                current_kill.sec = DemoParser.get_seconds(
                    current_round.start_tick, current_kill.tick
                )
                # Second block
                second_block = split_line[2].split(",")
                current_kill.victim_x_viz = float(second_block[0])
                current_kill.victim_y_viz = float(second_block[1].strip())
                current_kill.victim_view_x = float(second_block[2].strip())
                current_kill.victim_view_y = float(second_block[3].strip())
                current_kill.victim_area_name = second_block[4].strip()
                # Third block
                third_block = split_line[3].split(",")
                current_kill.attacker_x_viz = float(third_block[0])
                current_kill.attacker_y_viz = float(third_block[1].strip())
                current_kill.attacker_view_x = float(third_block[2].strip())
                current_kill.attacker_view_y = float(third_block[3].strip())
                current_kill.attacker_area_name = third_block[4].strip()
                # Fourth block
                fourth_block = split_line[4].split(",")
                current_kill.assister_x_viz = float(fourth_block[0])
                current_kill.assister_y_viz = float(fourth_block[1].strip())
                current_kill.assister_view_x = float(fourth_block[2].strip())
                current_kill.assister_view_y = float(fourth_block[3].strip())
                current_kill.assister_area_name = fourth_block[4].strip()
                # Fifth block
                fifth_block = split_line[5].split(",")
                current_kill.victim_id = int(fifth_block[0])
                current_kill.victim_name = fifth_block[1].strip()
                current_kill.victim_side = fifth_block[2].strip()
                # Sixth block
                sixth_block = split_line[6].split(",")
                current_kill.attacker_id = int(sixth_block[0])
                current_kill.attacker_name = sixth_block[1].strip()
                current_kill.attacker_side = sixth_block[2].strip()
                # Seventh block
                seventh_block = split_line[7].split(",")
                current_kill.assister_id = int(seventh_block[0])
                current_kill.assister_name = seventh_block[1].strip()
                current_kill.assister_side = seventh_block[2].strip()
                # Eigth block
                eigth_block = split_line[8].split(",")
                current_kill.weapon_id = DemoParser.get_weapon(int(eigth_block[0]))
                current_kill.is_wallshot = int(eigth_block[1].strip())
                current_kill.is_flashed = eigth_block[2].strip()
                if current_kill.is_flashed == "true":
                    current_kill.is_flashed = 1
                else:
                    current_kill.is_flashed = 0
                current_kill.is_headshot = eigth_block[3].replace("]", "").strip()
                if current_kill.is_headshot == "true":
                    current_kill.is_headshot = 1
                else:
                    current_kill.is_headshot = 0
                # Add current damage to round
                current_kills_list.append(current_kill)
            
            if "[GRENADE]" in event:
                current_grenade = Grenade()
                split_line = event.split("] [")
                # First block
                current_grenade.tick = int(split_line[1])
                current_grenade.sec = DemoParser.get_seconds(
                    current_round.start_tick, current_grenade.tick
                )
                # Second block
                second_block = split_line[2].split(",")
                current_grenade.player_id = int(second_block[0].strip())
                current_grenade.player_x_viz = float(second_block[1].strip())
                current_grenade.player_y_viz = float(second_block[2].strip())
                current_grenade.player_name = second_block[3].strip()
                current_grenade.player_side = second_block[4].strip()
                
                # Third block
                third_block = split_line[3].split(",")
                current_grenade.nade_id = int(third_block[0].strip())
                current_grenade.nade_x_viz = float(third_block[1].strip())
                current_grenade.nade_y_viz = float(third_block[2].strip())
                current_grenade.nade_type = DemoParser.get_weapon(int(third_block[3].strip()))
                current_grenade.nade_info = third_block[4].strip()
                current_grenade.nade_area_name = third_block[5].replace("]", "").strip()
                # Add current grenades to round
                current_grenade_list.append(current_grenade)
                
            if "[ENEMIESFLASHED]" in event:
                current_flash = Flashed()
                split_line = event.split("] [")
                # First block
                current_flash.tick = int(split_line[1])
                current_flash.sec = DemoParser.get_seconds(
                    current_round.start_tick, current_flash.tick
                )
                # Second block
                second_block = split_line[2].split(",")
                current_flash.attacker_id = int(second_block[0].strip())
                current_flash.attacker_x_viz = float(second_block[1])
                current_flash.attacker_y_viz = float(second_block[2].strip())
                current_flash.attacker_name = second_block[3].strip()
                current_flash.attacker_side = second_block[4].strip()
                # Third block
                third_block = split_line[3].split(",")
                current_flash.victim_id = int(third_block[0].strip())
                current_flash.victim_x_viz = float(third_block[1])
                current_flash.victim_y_viz = float(third_block[2].strip())
                current_flash.victim_name = third_block[3].strip()
                current_flash.victim_side = third_block[4].replace("]", "").strip()
                # Add current damage to round
                current_enemiesflash_list.append(current_flash)
                
            if "[TEAMFLASHED]" in event:
                current_flash = Flashed()
                split_line = event.split("] [")
                # First block
                current_flash.tick = int(split_line[1])
                current_flash.sec = DemoParser.get_seconds(
                    current_round.start_tick, current_flash.tick
                )
                # Second block
                second_block = split_line[2].split(",")
                current_flash.attacker_id = int(second_block[0])
                current_flash.attacker_x_viz = float(second_block[1])
                current_flash.attacker_y_viz = float(second_block[2].strip())
                current_flash.attacker_name = second_block[3].strip()
                current_flash.attacker_side = second_block[4].strip()
                # Third block
                third_block = split_line[3].split(",")
                current_flash.victim_id = int(third_block[0])
                current_flash.victim_x_viz = float(third_block[1])
                current_flash.victim_y_viz = float(third_block[2].strip())
                current_flash.victim_name = third_block[3].strip()
                current_flash.victim_side = third_block[4].replace("]", "").strip()
                # Add current damage to round
                current_teamflash_list.append(current_flash)
                
            if "[PLAYER INFO]" in event:
                current_playerInfo = PlayerInfo()
                split_line = event.split("] [")
                # First block
                current_playerInfo.tick = int(split_line[1])
                current_playerInfo.sec = DemoParser.get_seconds(
                    current_round.start_tick, current_playerInfo.tick
                )
                # Second block
                second_block = split_line[2].split(",")
                current_playerInfo.player_id = int(second_block[0].strip())
                current_playerInfo.player_name = second_block[1].strip()
                current_playerInfo.player_x_viz = float(second_block[2])
                current_playerInfo.player_y_viz = float(second_block[3].strip())
                current_playerInfo.player_side = second_block[4].strip()
                current_playerInfo.player_x_view = float(second_block[5].strip())
                current_playerInfo.player_money = int(second_block[6].strip())
                current_playerInfo.player_health = int(second_block[7].strip())
                current_playerInfo.player_armor = int(second_block[8].strip())     
                current_playerInfo.player_weapon = second_block[9].replace("]", "").strip()  
                # Add current damage to round
                current_playerInfo_list.append(current_playerInfo)    
                
            if "[BOMB]" in event:
                current_bomb_event = BombEvent()
                split_line = event.split("] [")
                # First block
                current_bomb_event.tick = int(split_line[1])
                current_bomb_event.sec = DemoParser.get_seconds(
                    current_round.start_tick, current_bomb_event.tick
                )
                # Second block
                second_block = split_line[2].split(",")
                current_bomb_event.player_x_viz = float(second_block[0].strip())
                current_bomb_event.player_y_viz = float(second_block[1].strip())
                current_bomb_event.player_id = int(second_block[2].strip())
                current_bomb_event.player_name = second_block[3].strip()
                current_bomb_event.bomb_site = second_block[4].strip()
                current_bomb_event.bomb_info = second_block[5].replace("]", "").strip()

                # Add current damage to round
                current_bomb_events_list.append(current_bomb_event)
                          
            if "[ITEM PICKUP]" in event:
                current_itemPickup = ItemPickup()
                split_line = event.split("] [")
                # First block
                current_itemPickup.tick = int(split_line[1])
                current_itemPickup.sec = DemoParser.get_seconds(
                    current_round.start_tick, current_itemPickup.tick
                )
                # Second block
                second_block = split_line[2].split(",")
                current_itemPickup.player_id = int(second_block[0].strip())
                current_itemPickup.player_name = second_block[1].strip()
                current_itemPickup.player_x_viz = float(second_block[2])
                current_itemPickup.player_y_viz = float(second_block[3].strip())
                current_itemPickup.player_side = second_block[4].strip()
                current_itemPickup.weapon_pickup = second_block[5].replace("]", "").strip()
                # Add current damage to round
                current_itemPickup_list.append(current_itemPickup)
                

    def parse(self):
        """ Parse wrapper function, called by user, and returns dictionary of data frames. Takes no arguments.
        """
        self._parse_demofile()
        if not self.demo_error:
            self._parse_match()
            self.write_data()
            self.logger.info("Finished parsing...")
            return self.dataframes
        else:
            return "Match has parsing error"

    def write_grenades(self):
        """ Write grenade events to a Pandas dataframe
        """
        grenade_df_list = []
        for i, r in enumerate(self.rounds):
            grenades = r.grenades
            for g in grenades:
                grenade_df_list.append(
                    [
                        self.match_id,
                        r.map_name,
                        i + 1,
                        g.tick,
                        g.sec,
                        g.player_id,
                        g.player_x_viz,
                        g.player_y_viz,
                        g.player_name,
                        g.player_side,
                        g.nade_id,
                        g.nade_x_viz,
                        g.nade_y_viz,
                        g.nade_type,
                        g.nade_info,
                        g.nade_area_name,
                    ]
                )
        frame = pd.DataFrame(
            grenade_df_list,
            columns=[
                "MatchId",
                "MapName",
                "RoundNum",
                "Tick",
                "Second",
                "PlayerID",
                "PlayerXViz",
                "PlayerYViz",
                "PlayerName",
                "PlayerSide",
                "NadeID",
                "NadeXViz",
                "NadeYViz",
                "NadeType",
                "NadeInfo",
                "NadeArea",
            ],
        )
        
        # we need to clean the dataframe because we get to much "air" information
        # nade_info air = nade entity is active
        # if a smoke detonate, we still get air info until the smoke expires
        """newFrame = frame.loc[[0]]        
        i = 0
        nadeID_list = []
        
        for index, row in frame.iterrows():
            if row['NadeInfo'] == "create":
                nadeID_list.append(row['NadeID'])
                newFrame.loc[i] = row
                i = i + 1
            if row['NadeInfo'] == "explosion":
                nadeID_list.remove(row['NadeID'])
                newFrame.loc[i] = row
                i = i + 1
            if row['NadeInfo'] == "destroy":
                nadeID_list.remove(row['NadeID'])
                newFrame.loc[i] = row
                i = i + 1 
            
            if row['NadeInfo'] == "air" and row['NadeID'] in nadeID_list:
                newFrame.loc[i] = row
                i = i + 1"""
        frame = frame.drop_duplicates(subset=["NadeID", "NadeXViz", "NadeYViz"])
        self.logger.info("Clearing nade list...")
        self.grenades_df = frame
        
        

    def write_bomb_events(self):
        """ Write bomb events to a Pandas dataframe
        """
        bomb_df_list = []
        for i, r in enumerate(self.rounds):
            bomb_events = r.bomb_events
            for be in bomb_events:
                bomb_df_list.append(
                    [
                        self.match_id,
                        i + 1,
                        be.tick,
                        be.sec,
                        be.player_x_viz,
                        be.player_y_viz,
                        be.player_id,
                        be.player_name,
                        be.bomb_site,
                        be.bomb_info,
                    ]
                )
        self.bomb_df = pd.DataFrame(
            bomb_df_list,
            columns=[
                "MatchId",
                "RoundNum",
                "Tick",
                "Second",
                "PlayerXViz",
                "PlayerYViz",
                "PlayerId",
                "PlayerName",
                "BombSite",
                "BombInfo",
            ],
        )
        
        # if someone drops the bomb we get the player position not the bomb position
        # lets see wo picks up the bomb, get this position and update drop position
        guard_bomb = False
        idx = 0
        for index, row in self.bomb_df.iterrows():
            if row['BombInfo'] == "drop":
                guard_bomb = True
                idx = index
                
            if row['BombInfo'] == "pickup" and guard_bomb is True:
                self.bomb_df.at[idx,'PlayerXViz'] = row['PlayerXViz']
                self.bomb_df.at[idx,'PlayerYViz'] = row['PlayerYViz']
                guard_bomb = False

    def write_kills(self):
        """ Write kills to a Pandas dataframe
        """
        kills_df_list = []
        for i, r in enumerate(self.rounds):
            kills = r.kills
            for k in kills:
                kills_df_list.append(
                    [
                        self.match_id,
                        r.map_name,
                        i + 1,
                        k.tick,
                        k.sec,
                        k.victim_x_viz,
                        k.victim_y_viz,
                        k.victim_view_x,
                        k.victim_view_y,
                        k.victim_area_name,
                        k.attacker_x_viz,
                        k.attacker_y_viz,
                        k.attacker_view_x,
                        k.attacker_view_y,
                        k.attacker_area_name,
                        k.assister_x_viz,
                        k.assister_y_viz,
                        k.assister_view_x,
                        k.assister_view_y,
                        k.assister_area_name,
                        k.victim_id,
                        k.victim_name,
                        k.victim_side,
                        k.attacker_id,
                        k.attacker_name,
                        k.attacker_side,
                        k.assister_id,
                        k.assister_name,
                        k.assister_side,
                        k.weapon_id,
                        k.is_wallshot,
                        k.is_flashed,
                        k.is_headshot,
                    ]
                )
        self.kills_df = pd.DataFrame(
            kills_df_list,
            columns=[
                "MatchId",
                "MapName",
                "RoundNum",
                "Tick",
                "Second",
                "VictimXViz",
                "VictimYViz",
                "VictimViewX",
                "VictimViewY",
                "VictimAreaName",
                "AttackerXViz",
                "AttackerYViz",
                "AttackerViewX",
                "AttackerViewY",
                "AttackerAreaName",
                "AssisterXViz",
                "AssisterYViz",
                "AssisterViewX",
                "AssisterViewY",
                "AssisterAreaName",
                "VictimID",
                "VictimName",
                "VictimSide",
                "AttackerID",
                "AttackerName",
                "AttackerSide",
                "AssisterID",
                "AssisterName",
                "AssisterSide",
                "Weapon",
                "IsWallshot",
                "IsFlashed",
                "IsHeadshot",
            ],
        )

    def write_damages(self):
        """ Write damages to a Pandas dataframe
        """
        damages_df_list = []
        for i, r in enumerate(self.rounds):
            damages = r.damages
            for d in damages:
                damages_df_list.append(
                    [
                        self.match_id,
                        r.map_name,
                        i + 1,
                        d.tick,
                        d.sec,
                        d.victim_x_viz,
                        d.victim_y_viz,
                        d.victim_view_x,
                        d.victim_view_y,
                        d.victim_area_name,
                        d.attacker_x_viz,
                        d.attacker_y_viz,
                        d.attacker_view_x,
                        d.attacker_view_y,
                        d.attacker_area_name,
                        d.victim_id,
                        d.victim_name,
                        d.victim_side,     
                        d.attacker_id,
                        d.attacker_name,
                        d.attacker_side,
                        d.hp_damage,
                        d.kill_hp_damage,
                        d.armor_damage,
                        d.weapon_id,
                        d.hit_group,
                    ]
                )
        self.damages_df = pd.DataFrame(
            damages_df_list,
            columns=[
                "MatchId",
                "MapName",
                "RoundNum",
                "Tick",
                "Second",
                "VictimXViz",
                "VictimYViz",
                "VictimViewX",
                "VictimViewY",
                "VictimAreaName",
                "AttackerXViz",
                "AttackerYViz",
                "AttackerViewX",
                "AttackerViewY",
                "AttackerAreaName",
                "VictimID",
                "VictimName",
                "VictimSide",
                "AttackerID",
                "AttackerName",
                "AttackerSide",
                "HpDamage",
                "KillHpDamage",
                "ArmorDamage",
                "Weapon",
                "HitGroup",
            ],
        )

    def write_rounds(self):
        """ Write rounds to Pandas dataframe
        """
        round_df_list = []
        for i, r in enumerate(self.rounds):
            round_df_list.append(
                [
                    self.match_id,
                    r.map_name,
                    i + 1,
                    r.start_tick,
                    r.end_tick,
                    r.end_ct_score,
                    r.end_t_score,
                    r.start_t_score,
                    r.start_ct_score,
                    r.round_winner_side,
                    r.round_winner,
                    r.round_loser,
                    r.reason,
                    r.end_freezetime,
                    r.ct_cash_spent_total,
                    r.ct_cash_spent_round,
                    r.ct_eq_val,
                    r.t_cash_spent_total,
                    r.t_cash_spent_round,
                    r.t_eq_val,
                    r.ct_round_type,
                    r.t_round_type,
                ]
            )
        self.rounds_df = pd.DataFrame(
            round_df_list,
            columns=[
                "MatchId",
                "MapName",
                "RoundNum",
                "StartTick",
                "EndTick",
                "EndCTScore",
                "EndTScore",
                "StartTScore",
                "StartCTScore",
                "RoundWinnerSide",
                "RoundWinner",
                "RoundLoser",
                "Reason",
                "EndFreezetime",
                "CTCashSpentTotal",
                "CTCashSpentRound",
                "CTEqVal",
                "TCashSpentTotal",
                "TCashSpentRound",
                "TEqVal",
                "CTRoundType",
                "TRoundType",
            ],
        )
    
    def write_itempickup(self):
        """ Write Itempickups to a Pandas dataframe
        """
        item_itemPickup_df_list = []
        for i, r in enumerate(self.rounds):
            item_pickup = r.current_itemPickup
            for k in item_pickup:
                item_itemPickup_df_list.append(
                    [
                        self.match_id,
                        r.map_name,
                        i + 1,
                        k.tick,
                        k.sec,
                        k.player_id,
                        k.player_name,
                        k.player_x_viz,
                        k.player_y_viz,
                        k.player_side,
                        k.weapon_pickup,
                    ]
                )
        
        self.item_pickup_df = pd.DataFrame(
            item_itemPickup_df_list,
            columns=[
                "MatchId",
                "MapName",
                "RoundNum",
                "Tick",
                "Second",
                "PlayerID",
                "PlayerName",
                "PlayerXViz",
                "PlayerYViz",
                "PlayerSide",
                "WeaponPickup",
            ],
        )
      
    def write_flashed(self):
        """ Write Itempickups to a Pandas dataframe
        """
        enemiesflashed_df_list = []
        for i, r in enumerate(self.rounds):
            flashed = r.current_enemiesflash
            for k in flashed:
                enemiesflashed_df_list.append(
                    [
                        self.match_id,
                        r.map_name,
                        i + 1,
                        k.tick,
                        k.sec,
                        k.attacker_id,
                        k.attacker_x_viz,
                        k.attacker_y_viz,
                        k.attacker_name,
                        k.attacker_side,
                        k.victim_id,
                        k.victim_x_viz,
                        k.victim_y_viz,
                        k.victim_name,
                        k.victim_side,
                    ]
                )        
        self.enemiesflashed_df = pd.DataFrame(
            enemiesflashed_df_list,
            columns=[
                "MatchId",
                "MapName",
                "RoundNum",
                "Tick",
                "Second",
                "AttackerID",
                "AttackerXViz",
                "AttackerYViz",
                "AttackerName",
                "AttackerSide",
                "VictimID",
                "VictimXViz",
                "VictimYViz",
                "VictimName",
                "VictimSide",
            ],
        )
        
        teamflashed_df_list = []
        for i, r in enumerate(self.rounds):
            flashed = r.current_teamflash
            for k in flashed:
                teamflashed_df_list.append(
                    [
                        self.match_id,
                        r.map_name,
                        i + 1,
                        k.tick,
                        k.sec,
                        k.attacker_id,
                        k.attacker_x_viz,
                        k.attacker_y_viz,
                        k.attacker_name,
                        k.attacker_side,
                        k.victim_id,
                        k.victim_x_viz,
                        k.victim_y_viz,
                        k.victim_name,
                        k.victim_side,
                    ]
                )        
        self.teamflashed_df = pd.DataFrame(
            teamflashed_df_list,
            columns=[
                "MatchId",
                "MapName",
                "RoundNum",
                "Tick",
                "Second",
                "AttackerID",
                "AttackerXViz",
                "AttackerYViz",
                "AttackerName",
                "AttackerSide",
                "VictimID",
                "VictimXViz",
                "VictimYViz",
                "VictimName",
                "VictimSide",
            ],
        )
    
    def write_playerInfo(self):
        """ Write Itempickups to a Pandas dataframe
        """
        playerInfo_df_list = []
        for i, r in enumerate(self.rounds):
            info = r.current_playerInfo
            for k in info:
                playerInfo_df_list.append(
                    [
                        self.match_id,
                        r.map_name,
                        i + 1,
                        k.tick,
                        k.sec,
                        k.player_id,
                        k.player_name,
                        k.player_x_viz,
                        k.player_y_viz,
                        k.player_side,
                        k.player_x_view,
                        k.player_money,
                        k.player_health,
                        k.player_armor,
                        k.player_weapon,
                    ]
                )        
        self.playerInfo_df = pd.DataFrame(
            playerInfo_df_list,
            columns=[
                "MatchId",
                "MapName",
                "RoundNum",
                "Tick",
                "Second",
                "PlayerID",
                "PlayerName",
                "PlayerXViz",
                "PlayerYViz",
                "PlayerSide",
                "PlayerXView",
                "PlayerMoney",
                "PlayerHealth",
                "PlayerArmor",
                "PlayerWeapon",
            ],
        )
        
        
    def write_data(self):
        """ Wrapper function to write a dictionary of Pandas dataframes
        """
        self.dataframes = {}
        self.write_rounds()
        self.write_damages()
        self.write_kills()
        self.write_bomb_events()
        self.write_grenades()    
        self.write_flashed()
        self.write_playerInfo()
        self.write_itempickup()
        self.dataframes["Map"] = self.rounds[0].map_name
        self.dataframes["Rounds"] = self.rounds_df
        self.dataframes["Damages"] = self.damages_df
        self.dataframes["Kills"] = self.kills_df
        self.dataframes["Bomb"] = self.bomb_df
        self.dataframes["Grenades"] = self.grenades_df
        self.dataframes["EnemiesFlashed"] = self.enemiesflashed_df
        self.dataframes["TeamFlashed"] = self.teamflashed_df
        self.dataframes["PlayerInfo"] = self.playerInfo_df
        self.dataframes["ItemPickup"] = self.item_pickup_df
        return self.dataframes