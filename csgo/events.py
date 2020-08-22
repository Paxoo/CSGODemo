class PlayerInfo:
    """ 
    Detail a Granade event

   Attributes:
        tick (int)              : Game tick at time of kill
        sec (float)             : Seconds since round start
        player_id (int)         : Player's steamID
        player_name (int)       : Player's username
        player_x_viz (float)    : Player's X position for visualization
        player_y_viz (float)    : Player's Y position for visualization
        player_side (string)    : Player's side (T or CT)
        player_money (int)      : Player's money
        player_health (int)     : Player's health
        player_armor (int)      : Player's armor value
        player_weapon (string)  : Player's active weapon
    """
    
    def __init__(
        self,
        tick=0,
        sec=0,
        player_id=0,
        player_name="",
        player_x_viz=0,
        player_y_viz=0,
        player_side="",
        player_x_view=0,
        player_money=0,
        player_health=0,
        player_armor=0,
        player_weapon="",
    ):
        self.tick = tick
        self.sec = sec  
        self.player_id = player_id
        self.player_name = player_name
        self.player_x_viz = player_x_viz
        self.player_y_viz = player_y_viz
        self.player_side = player_side
        self.player_x_view = player_x_view
        self.player_money = player_money
        self.player_health = player_health
        self.player_armor = player_armor
        self.player_weapon = player_weapon


class Grenade:
    """ 
    Detail a Granade event

   Attributes:
        tick (int)              : Game tick at time of kill
        sec (float)             : Seconds since round start
        player_x_viz (float)    : Player's X position for visualization
        player_y_viz (float)    : Player's Y position for visualization
        player_name (int)       : Player's username
        player_side (string)    : Player's side (T or CT)
        nade_id (int)         : nade uniqueID (until it gets destroyed)
        nade_x_viz (float)    : nade X position for visualization
        nade_y_viz (float)    : nade Y position for visualization
        nade_type (int)       : nade type (smoke, HE, ...)
        nade_info (string)    : nade info (create, destroy, air)
        nade_area_name (int)  : nade area name from nav file
    """
    
    def __init__(
        self,
        tick=0,
        sec=0,
        player_id=0,
        player_x_viz=0,
        player_y_viz=0,
        player_name="",
        player_side="",
        nade_id=0,
        nade_x_viz=0,
        nade_y_viz=0,
        nade_type="",
        nade_info="",
        nade_area_name="",
    ):
        self.tick = tick
        self.sec = sec   
        self.player_id = player_id
        self.player_x_viz = player_x_viz
        self.player_y_viz = player_y_viz
        self.player_name = player_name
        self.player_side = player_side
        self.nade_id = nade_id
        self.nade_x_viz = nade_x_viz
        self.nade_y_viz = nade_y_viz
        self.nade_type = nade_type
        self.nade_info = nade_info
        self.nade_area_name = nade_area_name


class BombEvent:
    """ 
    Detail a Bomb Plant/Defuse event

    Attributes:
        tick (int)          : Game tick at time of event
        sec (float)         : Seconds since round start
        player_name (string): Player's username
        player_id (int)     : Player's steam id
        team (string)       : Player's team/clan name
        x (float)           : X position of bomb event
        y (float)           : Y position of bomb event
        z (float)           : Z position of bomb event
        area_id (int)       : Location of event as nav file area id
        bomb_site (string)  : Bomb site (A or B)
        event_type (string) : Plant, defuse, explode
    """

    def __init__(
        self,
        tick=0,
        sec=0,
        player_x_viz=0,
        player_y_viz=0,
        player_id=0,
        player_name="",
        bomb_site="",
        bomb_info="",
    ):
        self.tick = tick
        self.sec = sec
        self.player_x_viz = player_x_viz
        self.player_y_viz = player_y_viz
        self.player_id = player_id
        self.player_name = player_name
        self.bomb_site = bomb_site
        self.bomb_info = bomb_info


class Round:
    """ Detail a CSGO round

    Attributes:
        map_name (string)          : Round's map
        start_tick (int)           : Tick on ROUND START event
        end_tick (int)             : Tick on ROUND END event
        end_ct_score (int)         : Ending CT score
        end_t_score (int)          : Ending T score
        start_t_score (int)        : Starting T score
        start_ct_score (int)       : Starting CT score
        round_winner_side (string) : T/CT for round winner
        round_winner (string)      : Winning team name
        round_loser (string)       : Losing team name
        reason (int)               : Corresponds to how the team won (defuse, killed other team, etc.)
        ct_cash_spent_total (int)  : CT total cash spent by this point of the game
        ct_cash_spent_round (int)  : CT total cash spent in current round
        ct_eq_val (int)            : CT equipment value at end of freezetime
        t_cash_spent_total (int)   : T total cash spent by this point of the game
        t_cash_spent_round (int)   : T total cash spent in current round
        t_eq_val (int)             : T equipment value at end of freezetime
        ct_round_type (string)     : CT round buy type
        t_round_type (string)      : T round buy type
        bomb_plant_tick            : Bomb plant tick
        bomb_events (list)         : List of BombEvent objects
        damages (list)             : List of Damage objects
        kills (list)               : List of Kill objects
        footstep (list)            : List of Footstep objects
        grenades (list)            : List of Grenade objects
    """

    def __init__(
        self,
        map_name="",
        start_tick=0,
        end_tick=0,
        end_ct_score=0,
        end_t_score=0,
        start_ct_score=0,
        start_t_score=0,
        round_winner_side="",
        round_winner="",
        round_loser="",
        reason=0,
        ct_cash_spent_total=0,
        ct_cash_spent_round=0,
        ct_eq_val=0,
        t_cash_spent_total=0,
        t_cash_spent_round=0,
        t_eq_val=0,
        ct_round_type="",
        t_round_type="",
        bomb_plant_tick=0,
        end_freezetime=0,
        players=[],
        kills=[],
        damages=[],
        footsteps=[],
        bomb_events=[],
        grenades=[],
        current_itemPickup =[],
        current_playerInfo = [],
    ):
        self.map_name = map_name
        self.start_tick = start_tick
        self.end_tick = end_tick
        self.end_ct_score = end_ct_score
        self.end_t_score = end_t_score
        self.start_ct_score = start_ct_score
        self.start_t_score = start_t_score
        self.round_winner_side = round_winner_side
        self.round_winner = round_winner
        self.round_loser = round_loser
        self.end_freezetime = end_freezetime
        self.reason = reason
        self.players = players
        self.kills = kills
        self.damages = damages
        self.footsteps = footsteps
        self.bomb_events = bomb_events
        self.grenades = grenades
        self.ct_cash_spent_total = ct_cash_spent_total
        self.ct_cash_spent_round = ct_cash_spent_round
        self.ct_eq_val = ct_eq_val
        self.t_cash_spent_total = t_cash_spent_total
        self.t_cash_spent_round = t_cash_spent_round
        self.t_eq_val = t_eq_val
        self.ct_round_type = ct_round_type
        self.t_round_type = t_round_type
        self.bomb_plant_tick = bomb_plant_tick
        self.current_itemPickup_list = current_itemPickup
        self.current_playerInfo = current_playerInfo
        if self.round_winner_side == "CT":
            self.start_ct_score = self.end_ct_score - 1
            self.start_t_score = self.start_t_score
        if self.round_winner_side == "T":
            self.start_ct_score = self.end_ct_score
            self.start_t_score = self.start_t_score - 1


class Kill:
    """ Detail a kill event

    Attributes:
        tick (int)                : Game tick at time of kill
        sec (float)               : Seconds since round start
        victim_x_viz (float)      : Victim's X position for visualization
        victim_y_viz (float)      : Victim's Y position for visualization
        victim_view_x (float)     : Victim's X view
        victim_view_y (float)     : Victim's Y view
        victim_area_name (int)    : Victim's area name from nav file
        attacker_x_viz (float)    : Attacker's X position for visualization
        attacker_y_viz (float)    : Attacker's Y position for visualization
        attacker_view_x (float)   : Attacker's X view
        attacker_view_y (float)   : Attacker's Y view
        attacker_area_name (int)  : Attacker's area name from nav file
        assister_x_viz (float)    : Assister's X position for visualization
        assister_y_viz (float)    : Assister's Y position for visualization
        assister_view_x (float)   : Assister's X view
        assister_view_y (float)   : Assister's Y view
        assister_area_name (int)  : Assister's area name from nav file
        victim_id (int)           : Victim's steam id
        victim_name (string)      : Victim's username
        victim_side (string)      : Victim's side (T or CT)
        victim_team_eq_val (int)  : Victim team's starting equipment value
        attacker_id (int)         : Attacker's steam id
        attacker_name (int)       : Attacker's username
        attacker_side (string)    : Attacker's side (T or CT)
        attacker_team_eq_val (int): Attacker team's starting equipment value
        assister_id (int)         : Assister's steam id
        assister_name (int)       : Assister's username
        assister_side (string)    : Assister's side (T or CT)
        weapon_id (int)           : Weapon id
        is_wallshot (boolean)     : If kill was a wallshot then 1, 0 otherwise
        is_flashed (boolean)      : If kill victim was flashed then 1, 0 otherwise
        is_headshot (boolean)     : If kill was a headshot then 1, 0 otherwise
    """

    def __init__(
        self,
        tick=0,
        sec=0,
        victim_x_viz=0,
        victim_y_viz=0,
        victim_view_x=0,
        victim_view_y=0,
        victim_area_name="",
        attacker_x_viz=0,
        attacker_y_viz=0,
        attacker_view_x=0,
        attacker_view_y=0,
        attacker_area_name="",
        assister_x_viz=0,
        assister_y_viz=0,
        assister_view_x=0,
        assister_view_y=0,
        assister_area_name="",
        victim_id=0,
        victim_name="",
        victim_side="",
        attacker_id=0,
        attacker_name="",
        attacker_side="",
        assister_id=0,
        assister_name="",
        assister_side="",
        weapon_id=0,
        is_wallshot=False,
        is_flashed=False,
        is_headshot=False,
    ):
        self.tick = tick
        self.sec = sec
        self.attacker_id = attacker_id
        self.attacker_name = attacker_name
        self.attacker_side = attacker_side
        self.attacker_x_viz = attacker_x_viz
        self.attacker_y_viz = attacker_y_viz
        self.attacker_view_x = attacker_view_x
        self.attacker_view_y = attacker_view_y
        self.attacker_area_name = attacker_area_name
        self.victim_id = victim_id
        self.victim_name = victim_name
        self.victim_side = victim_side
        self.victim_x_viz = victim_x_viz
        self.victim_y_viz = victim_y_viz
        self.victim_view_x = victim_view_x
        self.victim_view_y = victim_view_y
        self.victim_area_name = victim_area_name
        self.assister_id = assister_id
        self.assister_name = assister_name
        self.assister_side = assister_side
        self.assister_x_viz = assister_x_viz
        self.assister_y_viz = assister_y_viz
        self.assister_view_x = assister_view_x
        self.assister_view_y = assister_view_y
        self.assister_area_name = assister_area_name
        self.weapon_id = weapon_id
        self.is_wallshot = is_wallshot
        self.is_flashed = is_flashed
        self.is_headshot = is_headshot


class Damage:
    """ Detail a damage event

    Attributes:
        tick (int)                : Game tick at time of kill
        sec (float)               : Seconds since round start
        victim_x_viz (float)      : Victim's X position for visualization
        victim_y_viz (float)      : Victim's Y position for visualization
        victim_view_x (float)     : Victim's X view
        victim_view_y (float)     : Victim's Y view
        victim_area_name (int)    : Victim's area name from nav file
        attacker_x_viz (float)    : Attacker's X position for visualization
        attacker_y_viz (float)    : Attacker's Y position for visualization
        attacker_view_x (float)   : Attacker's X view
        attacker_view_y (float)   : Attacker's Y view
        attacker_area_name (int)  : Attacker's area name from nav file
        victim_id (int)           : Victim's steam id
        victim_name (string)      : Victim's username
        victim_side (string)      : Victim's side (T or CT)
        attacker_id (int)         : Attacker's steam id
        attacker_name (int)       : Attacker's username
        attacker_side (string)    : Attacker's side (T or CT)
        hp_damage (int)           : HP damage dealt
        kill_hp_damage (int)      : HP damage dealt normalized to 100.
        armor_damage (int)        : Armor damage dealt
        weapon_id (int)           : Weapon id
        hit_group (int)           : Hit group
    """

    def __init__(
        self,
        tick=0,
        sec=0,
        victim_x_viz=0,
        victim_y_viz=0,
        victim_view_x=0,
        victim_view_y=0,
        victim_area_name="",
        attacker_x_viz=0,
        attacker_y_viz=0,
        attacker_view_x=0,
        attacker_view_y=0,
        attacker_area_name="",
        victim_id=0,
        victim_name="",
        victim_side="",
        attacker_id=0,
        attacker_name="",
        attacker_side="",
        hp_damage=0,
        kill_hp_damage=0,
        armor_damage=0,
        weapon_id=0,
        hit_group=0,
    ):
        self.tick = tick
        self.sec = sec
        self.victim_x_viz = victim_x_viz
        self.victim_y_viz = victim_y_viz
        self.victim_view_x = victim_view_x
        self.victim_view_y = victim_view_y
        self.victim_area_name = victim_area_name
        self.attacker_x_viz = attacker_x_viz
        self.attacker_y_viz = attacker_y_viz
        self.attacker_view_x = attacker_view_x
        self.attacker_view_y = attacker_view_y
        self.attacker_area_name = attacker_area_name
        self.victim_id = victim_id
        self.victim_name = victim_name
        self.victim_side = victim_side
        self.attacker_id = attacker_id
        self.attacker_name = attacker_name
        self.attacker_side = attacker_side
        self.hp_damage = hp_damage
        self.kill_hp_damage = kill_hp_damage
        self.armor_damage = armor_damage
        self.weapon_id = weapon_id
        self.hit_group = hit_group

class Flashed:
    """ Detail a Flashed event
    
    Attributes:
        tick (int)              : Game tick at time of kill
        sec (float)             : Seconds since round start
        attacker_x_viz (float)  : Attacker's X position for visualization
        attacker_y_viz (float)  : Attacker's Y position for visualization
        attacker_name (string)  : Attacker's Name
        attacker_team (string)  : Attacker's team/clan name
        attacker_side (string)  : Attacker's side (T or CT)
        victim_x_viz (float)    : Victim's X position for visualization
        victim_y_viz (float)    : Victim's Y position for visualization
        victim_name (string)    : Victim's Name
        victim_team (string)    : Victim's team/clan name
        victim_side (string)    : Victim's side (T or CT)
    """

    def __init__(
        self,
        tick=0,
        sec=0,
        attacker_id=0,
        attacker_x_viz=0,
        attacker_y_viz=0,
        attacker_name="",
        attacker_side="",
        victim_id=0,
        victim_x_viz=0,
        victim_y_viz=0,
        victim_name="",
        victim_side="",
    ):
        self.tick = tick
        self.sec = sec
        self.attacker_id = attacker_id
        self.attacker_x_viz = attacker_x_viz
        self.attacker_y_viz = attacker_y_viz
        self.attacker_name = attacker_name
        self.attacker_side = attacker_side
        self.victim_id = victim_id
        self.victim_x_viz = victim_x_viz
        self.victim_y_viz = victim_y_viz
        self.victim_name = victim_name
        self.victim_side = victim_side

class ItemPickup:
    """ Detail a ItemPickup event

    Attributes:
        tick (int)              : Game tick at time of kill
        sec (float)             : Seconds since round start
        player_x_viz (float)    : Player's X position for visualization
        player_y_viz (float)    : Player's Y position for visualization
        player_view_x (float)   : Player's X view
        player_view_y (float)   : Player's Y view
        player_area_id (int)    : Player's area id from nav file
        player_area_name (int)  : Player's area name from nav file
        player_id (int)         : Player's steam id
        player_name (int)       : Player's username
        player_team (string)    : Player's team/clan name
        player_side (string)    : Player's side (T or CT)
        weapon_id (int)         : Weapon id
    """

    def __init__(
        self,
        tick=0,
        sec=0,
        player_id=0, 
        player_name="",
        player_x_viz=0,
        player_y_viz=0,
        player_side="",
        weapon_pickup="",
    ):
        self.tick = tick
        self.sec = sec
        self.player_id = player_id
        self.player_name = player_name
        self.player_x_viz = player_x_viz
        self.player_y_viz = player_y_viz
        self.player_side = player_side
        self.weapon_pickup = weapon_pickup
