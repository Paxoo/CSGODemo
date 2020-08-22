package main

import (
	"fmt"
	"os"

	dem "github.com/markus-wa/demoinfocs-golang/v2/pkg/demoinfocs"
	common "github.com/markus-wa/demoinfocs-golang/v2/pkg/demoinfocs/common"
	events "github.com/markus-wa/demoinfocs-golang/v2/pkg/demoinfocs/events"
	ex "github.com/markus-wa/demoinfocs-golang/v2/examples"
    metadata "github.com/markus-wa/demoinfocs-golang/v2/pkg/demoinfocs/metadata"
	gonav "github.com/pnxenopoulos/csgonavparse"
)


// Run parser as follows: go run parse_demofile.go -demo /path/to/demo.dem
func main() {
	// Read in demofile
	f, err := os.Open(ex.DemoPathFromArgs())
	defer f.Close()
	checkError(err)

	// Create new demoparser
	p := dem.NewParser(f)

	// Parse demofile header
	header, err := p.ParseHeader()
	checkError(err)

	// Get nav mesh given the map name

	currentMap := header.MapName
    mapMetadata := metadata.MapNameToMap[currentMap]

    fNav, _ := os.Open("../data/nav/" + currentMap + ".nav")
	parserNav := gonav.Parser{Reader: fNav}
	mesh, _ := parserNav.Parse()
    
    
    updateRate := (int(header.FrameRate()) + 1) / 4  // frames per second / 4 -> get info every 250ms
    fmt.Printf("[updaterate] [%d] \n", updateRate) 
    if updateRate >= 0 && updateRate <= 5 {
        updateRate = 32
    }
    
    frame_count := 0
    roundStarted := 0
    freezetimeOver := false
    
	p.RegisterEventHandler(func(e events.RoundStart) {
		// Parse round start events
		gs := p.GameState()
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup rounds
		if (warmup == false) && (roundStarted == 0) {
						
			fmt.Printf("[ROUND START] [%s, %d] [%d, %d] \n", header.MapName, gs.IngameTick(), gs.TeamTerrorists().Score(), gs.TeamCounterTerrorists().Score())
    		roundStarted = 1
    	}
	})

	p.RegisterEventHandler(func(e events.RoundEnd) {
		/* Parse round end events
		 */
		gs := p.GameState()
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup rounds
		if (warmup == false) && (roundStarted == 1) {

			fmt.Printf("[ROUND PURCHASE] [%s, %d] [T, %d, %d, %d] [CT, %d, %d, %d] \n",
				header.MapName, gs.IngameTick(),
				gs.TeamTerrorists().MoneySpentTotal(),
				gs.TeamTerrorists().MoneySpentThisRound(),
				gs.TeamTerrorists().FreezeTimeEndEquipmentValue(),
				gs.TeamCounterTerrorists().MoneySpentTotal(),
				gs.TeamCounterTerrorists().MoneySpentThisRound(),
				gs.TeamCounterTerrorists().FreezeTimeEndEquipmentValue(),
			)

			switch e.Winner {
			case common.TeamTerrorists:
				// Winner's score + 1 because it hasn't actually been updated yet
				fmt.Printf("[ROUND END] [%s, %d] [%d, %d] [T, %s, %s, %d] \n", header.MapName, gs.IngameTick(), gs.TeamTerrorists().Score()+1, gs.TeamCounterTerrorists().Score(), gs.TeamTerrorists().ClanName(), gs.TeamCounterTerrorists().ClanName(), e.Reason)
			case common.TeamCounterTerrorists:
				fmt.Printf("[ROUND END] [%s, %d] [%d, %d] [CT, %s, %s, %d] \n", header.MapName, gs.IngameTick(), gs.TeamTerrorists().Score(), gs.TeamCounterTerrorists().Score()+1, gs.TeamCounterTerrorists().ClanName(), gs.TeamTerrorists().ClanName(), e.Reason)
			default:
				/* It is currently unknown why rounds may end as draws. Markuswa
				suggested that it may be due to match medic. [NOTE]
				*/
				fmt.Printf("[ROUND END] [%s, %d] DRAW \n", header.MapName, gs.IngameTick())
			}
            roundStarted = 0
            freezetimeOver = false
		}
	})

	p.RegisterEventHandler(func(e events.RoundEndOfficial) {
		// Parse official round end
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup rounds
		if (warmup == false)  {
			fmt.Printf("[ROUND END OFFICIAL] [%s, %d] \n", header.MapName, p.GameState().IngameTick())
		}
	})

	p.RegisterEventHandler(func(e events.MatchStart) {
		// Parse match start events
		// 99dmg demo doesnt contain matchstart - strange
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup match starts
		if warmup == false {
			fmt.Printf("[MATCH START] [%s, %d] \n", header.MapName, p.GameState().IngameTick())
			roundStarted = 1
		}
	})
	
	p.RegisterEventHandler(func(e events.RoundFreezetimeEnd) {
		// Parse end of freezetime
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup rounds
		if (warmup == false) && (roundStarted == 1) {
			fmt.Printf("[FREEZE END] [%d] \n", p.GameState().IngameTick())
			freezetimeOver = true
		}
	})
	
	p.RegisterEventHandler(func(e events.FrameDone) {
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup rounds
		if (warmup == false) && (roundStarted == 1) {
    		if frame_count == updateRate {
    			// nade info
        		var nadeID int64 = 0
    			var nadePosXViz float64 = 0.0
    			var nadePosYViz float64 = 0.0
    			var nadeAreaPlace string = "NA"
    			
    			// player info
    			var playerSideString string = "NA"
    			
        		gameTick := p.GameState().IngameTick()
            
                if freezetimeOver == true {
                    // get player Position
                    for _, player := range p.GameState().Participants().Playing() {
                        if player.IsAlive() == true {                   
                            playerPosXViz, playerPosYViz := mapMetadata.TranslateScale(player.Position().X, player.Position().Y) 
                            if player.Team == 2 {
            					playerSideString = "T"
            				} else if player.Team == 3 {
            					playerSideString = "CT"
            				}
                            
                            playerID := player.SteamID64
                            playerName := player.Name
                            playerXView := player.ViewDirectionX()
                            playerMoney := player.Money()
                            playerHealth := player.Health()
                            playerArmor := player.Armor()
                            playerWeapon := player.ActiveWeapon()
                            
                            fmt.Printf("[PLAYER INFO] [%d] [%d, %s, %f, %f, %s, %f, %d, %d, %d, %s] \n", 
                                gameTick,
                                playerID, playerName, playerPosXViz, playerPosYViz, playerSideString, playerXView,
                                playerMoney, playerHealth, playerArmor, playerWeapon)
                        }
                    }
                }
                
                // get active nades flying through the air tonight
                for _, nade := range p.GameState().GrenadeProjectiles() {
                    // ignore decoy
                    if nade.WeaponInstance.Type != 501 {
                        nadePosXViz, nadePosYViz = mapMetadata.TranslateScale(nade.Trajectory[len(nade.Trajectory)-1].X, nade.Trajectory[len(nade.Trajectory)-1].Y)
            			nadePosPoint := gonav.Vector3{X: float32(nade.Trajectory[len(nade.Trajectory)-1].X), Y: float32(nade.Trajectory[len(nade.Trajectory)-1].Y), Z: float32(nade.Trajectory[len(nade.Trajectory)-1].Z)}
            			nadeArea := mesh.GetNearestArea(nadePosPoint, true)
            			if nadeArea != nil {
            				if nadeArea.Place != nil {
            					nadeAreaPlace = nadeArea.Place.Name
            				}
            			}
                		grenadeType := nade.WeaponInstance.Type
                		nadeID = nade.WeaponInstance.UniqueID() 
                        
                        // player
                        playerPosXViz, playerPosYViz := mapMetadata.TranslateScale(nade.Thrower.Position().X, nade.Thrower.Position().Y)
                        playerName := nade.Thrower.Name
                        if nade.Thrower.Team == 2 {
        					playerSideString = "T"
        				} else if nade.Thrower.Team == 3 {
        					playerSideString = "CT"
        				}
                        
                        playerID := nade.Thrower.SteamID64            	
                        fmt.Printf("[GRENADE] [%d] [%d, %f, %f, %s, %s] [%d, %f, %f, %d, %s, %s]\n",
             			    gameTick,
             			    playerID, playerPosXViz, playerPosYViz, playerName, playerSideString,
             			    nadeID, nadePosXViz, nadePosYViz, grenadeType, "air", nadeAreaPlace) 
     			    }
                }

        		frame_count = 0
    		}else{
                frame_count = frame_count + 1 		
    		}
		}
	})
	
	p.RegisterEventHandler(func(e events.ItemEquip) {
		// gets triggerd if someone is switching to a weapon
		// we activate this event after the freezetime, because player like to switch
		// their weapons alot during freezetime
		
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup rounds
		if (warmup == false) && (roundStarted == 1) && (freezetimeOver == true){
    		gameTick := p.GameState().IngameTick()
    		
    		var playerSideString string = "NA"
    		
    		playerPosXViz, playerPosYViz := mapMetadata.TranslateScale(e.Player.Position().X, e.Player.Position().Y) 
            if e.Player.Team == 2 {
					playerSideString = "T"
				} else if e.Player.Team == 3 {
					playerSideString = "CT"
				}
            
            playerID := e.Player.SteamID64
            playerName := e.Player.Name
            playerXView := e.Player.ViewDirectionX()
            playerMoney := e.Player.Money()
            playerHealth := e.Player.Health()
            playerArmor := e.Player.Armor()
            playerWeapon := e.Player.ActiveWeapon()
            
    		fmt.Printf("[PLAYER INFO] [%d] [%d, %s, %f, %f, %s, %f, %d, %d, %d, %s] \n", 
                gameTick,
                playerID, playerName, playerPosXViz, playerPosYViz, playerSideString, playerXView,
                playerMoney, playerHealth, playerArmor, playerWeapon)
		
		}
	})
	
	p.RegisterEventHandler(func(e events.ItemPickup ) {
		// gets triggert if someone picks up a new item, either by buying or walking over it
		// thats why we ignore knife and bomb - roundstart
		
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup rounds
		if (warmup == false) && (roundStarted == 1){
    		// ignore 405 = knife, 404 = bomb
    		if (e.Weapon.Type != 405) && (e.Weapon.Type != 404) {
        		gameTick := p.GameState().IngameTick()
        		var playerSideString string = "NA" 
        		
        		if e.Player.Team == 2 {
					playerSideString = "T"
				} else if e.Player.Team == 3 {
					playerSideString = "CT"
				}
        		playerID := e.Player.SteamID64
                playerName := e.Player.Name
                playerPosXViz, playerPosYViz := mapMetadata.TranslateScale(e.Player.Position().X, e.Player.Position().Y) 
                weaponPickup := e.Weapon.Type
                
    			fmt.Printf("[ITEM PICKUP] [%d] [%d, %s, %f, %f, %s, %s] \n", 
    			gameTick, 
    			playerID, playerName, playerPosXViz, playerPosYViz, playerSideString, weaponPickup)
    		}
		}
	})
	
	p.RegisterEventHandler(func(e events.PlayerHurt) {
		// Parse player damage events
		
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup player hurt events
		if (warmup == false) && (roundStarted == 1) {
			// First block (game state)
			gameTick := p.GameState().IngameTick()
			var mapName string = header.MapName

			// Second block (victim location)
			var victimX float64 = 0.0
			var victimY float64 = 0.0
			var victimZ float64 = 0.0
			var VictimXViz float64 = 0.0
			var VictimYViz float64 = 0.0
			var VictimClosestAreaName string = "NA"
			var VictimViewX float32 = 0.0
			var VictimViewY float32 = 0.0

			// Third block (attacker location)
			var attackerX float64 = 0.0
			var attackerY float64 = 0.0
			var attackerZ float64 = 0.0
			var attackerXViz float64 = 0.0
			var attackerYViz float64 = 0.0
			var attackerClosestAreaName string = "NA"
			var attackerViewX float32 = 0.0
			var attackerViewY float32 = 0.0

			// Fourth block (victim player/team)
			var victimID uint64 = 0
			var victimName string = "NA"
			var victimSideString string = "NA"

			// Fifth block (attacker player/team)
			var attackerID uint64 = 0
			var attackerName string = "NA"
			var attackerSideString string = "NA"

			// Sixth block (Damage/Weapon)
			hpDmg := e.HealthDamage
			KillHpDmg := hpDmg

			// If a player has more than 100 damage taken, squash this value back
			//down to 100. This may need to be changed in the future. [NOTE]
			if hpDmg > 100 {
				KillHpDmg = 100
			}
			armorDmg := e.ArmorDamage
			weaponID := e.Weapon.Type
			hitGroup := e.HitGroup

			// Find victim values
			if e.Player == nil {
				victimID = 0
			} else {
				victimID = e.Player.SteamID64
				victimX = e.Player.Position().X
				victimY = e.Player.Position().Y
				victimZ = e.Player.Position().Z
				VictimXViz, VictimYViz = mapMetadata.TranslateScale(victimX, victimY)
				VictimViewX = e.Player.ViewDirectionX()
				VictimViewY = e.Player.ViewDirectionY()
				victimLoc := gonav.Vector3{X: float32(victimX), Y: float32(victimY), Z: float32(victimZ)}
				victimArea := mesh.GetNearestArea(victimLoc, true)
				if victimArea != nil {
					if victimArea.Place != nil {
						VictimClosestAreaName = victimArea.Place.Name
					}
				}
				victimName = e.Player.Name
				if e.Player.Team == 2 {
					victimSideString = "T"
				} else if e.Player.Team == 3 {
					victimSideString = "CT"
				}
			}

			// Find attacker values
			if e.Attacker == nil {
				attackerID = 0
			} else {
				attackerID = e.Attacker.SteamID64
				attackerX = e.Attacker.Position().X
				attackerY = e.Attacker.Position().Y
				attackerZ = e.Attacker.Position().Z
				attackerXViz, attackerYViz = mapMetadata.TranslateScale(attackerX, attackerY)
				attackerViewX = e.Attacker.ViewDirectionX()
				attackerViewY = e.Attacker.ViewDirectionY()
				attackerLoc := gonav.Vector3{X: float32(attackerX), Y: float32(attackerY), Z: float32(attackerZ)}
				attackerArea := mesh.GetNearestArea(attackerLoc, true)
				if attackerArea != nil {
					if attackerArea.Place != nil {
						attackerClosestAreaName = attackerArea.Place.Name
					}
				}
				attackerName = e.Attacker.Name
				if e.Attacker.Team == 2 {
					attackerSideString = "T"
				} else if e.Attacker.Team == 3 {
					attackerSideString = "CT"
				}
			}

			// Print a line of the damage information
			fmt.Printf("[DAMAGE] [%s, %d] [%f, %f, %f, %f, %s] [%f, %f, %f, %f, %s] [%d, %s, %s] [%d, %s, %s] [%d, %d, %d, %d, %d] \n",
				mapName, gameTick,
				VictimXViz, VictimYViz, VictimViewX, VictimViewY,  VictimClosestAreaName,
				attackerXViz, attackerYViz, attackerViewX, attackerViewY, attackerClosestAreaName,
				victimID, victimName, victimSideString,
				attackerID, attackerName, attackerSideString,
				hpDmg, KillHpDmg, armorDmg, weaponID, hitGroup)
		}
	})

    
    p.RegisterEventHandler(func(e events.HeExplode) {
		// HE explodes

		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup grenade events
		if (warmup == false) && (roundStarted == 1) {
			gameTick := p.GameState().IngameTick()
    	    
    	    // Second block (player info)
    	    var playerID uint64 = 0
			var playerPosXViz float64 = 0.0
			var playerPosYViz float64 = 0.0
			var playerName string = "NA"
			var playerSideString string = "NA"
			var playerAreaPlace string = "NA"
					
			// Third block (nade info)
			var nadeID int64 = 0
			var nadePosXViz float64 = 0.0
			var nadePosYViz float64 = 0.0
			var nadeAreaPlace string = "NA"	
			
    	    // get player information
    	    if e.Thrower != nil {
    			playerName = e.Thrower.Name
    			playerPosXViz, playerPosYViz = mapMetadata.TranslateScale(e.Thrower.Position().X, e.Thrower.Position().Y)				
				playerPosPoint := gonav.Vector3{X: float32(e.Thrower.Position().X), Y: float32(e.Thrower.Position().Y), Z: float32(e.Thrower.Position().Z)}
				playerArea := mesh.GetNearestArea(playerPosPoint, true)
				
				if playerArea != nil {
					if playerArea.Place != nil {
						playerAreaPlace = playerArea.Place.Name
					}
				}		
				if e.Thrower.Team == 2 {
					playerSideString = "T"
				} else if e.Thrower.Team == 3 {
					playerSideString = "CT"
				}
				playerID = e.Thrower.SteamID64
    	    }

    		// get nade information   	    
    	    nadePosXViz, nadePosYViz = mapMetadata.TranslateScale(e.Base().Position.X, e.Base().Position.Y)
			nadePosPoint := gonav.Vector3{X: float32(e.Base().Position.X), Y: float32(e.Base().Position.Y), Z: float32(e.Base().Position.Z)}
			nadeArea := mesh.GetNearestArea(nadePosPoint, true)
			if nadeArea != nil {
				if nadeArea.Place != nil {
					nadeAreaPlace = nadeArea.Place.Name
				}
			}		
			grenadeType := e.Base().GrenadeType
			nadeID = e.Base().Grenade.UniqueID()
            
			fmt.Printf("[GRENADE] [%d] [%d, %f, %f, %s, %s, %s] [%d, %f, %f, %d, %s, %s]\n",
 			    gameTick,
 			    playerID, playerPosXViz, playerPosYViz, playerName, playerSideString, playerAreaPlace,
 			    nadeID, nadePosXViz, nadePosYViz, grenadeType, "explosion", nadeAreaPlace)
		}
	})
	
    p.RegisterEventHandler(func(e events.FlashExplode) {
    	// Flash explodes

		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup grenade events
		if (warmup == false) && (roundStarted == 1) {
			gameTick := p.GameState().IngameTick()
    	    
    	    // Second block (player info)
    	    var playerID uint64 = 0
			var playerPosXViz float64 = 0.0
			var playerPosYViz float64 = 0.0
			var playerName string = "NA"
			var playerSideString string = "NA"
			var playerAreaPlace string = "NA"
					
			// Third block (nade info)
			var nadeID int64 = 0
			var nadePosXViz float64 = 0.0
			var nadePosYViz float64 = 0.0
			var nadeAreaPlace string = "NA"	
			
    	    // get player information
    	    if e.Thrower != nil {
    			playerName = e.Thrower.Name
    			playerPosXViz, playerPosYViz = mapMetadata.TranslateScale(e.Thrower.Position().X, e.Thrower.Position().Y)				
				playerPosPoint := gonav.Vector3{X: float32(e.Thrower.Position().X), Y: float32(e.Thrower.Position().Y), Z: float32(e.Thrower.Position().Z)}
				playerArea := mesh.GetNearestArea(playerPosPoint, true)
				
				if playerArea != nil {
					if playerArea.Place != nil {
						playerAreaPlace = playerArea.Place.Name
					}
				}		
				if e.Thrower.Team == 2 {
					playerSideString = "T"
				} else if e.Thrower.Team == 3 {
					playerSideString = "CT"
				}
				playerID = e.Thrower.SteamID64
    	    }

    		// get nade information   	    
    	    nadePosXViz, nadePosYViz = mapMetadata.TranslateScale(e.Base().Position.X, e.Base().Position.Y)
			nadePosPoint := gonav.Vector3{X: float32(e.Base().Position.X), Y: float32(e.Base().Position.Y), Z: float32(e.Base().Position.Z)}
			nadeArea := mesh.GetNearestArea(nadePosPoint, true)
			if nadeArea != nil {
				if nadeArea.Place != nil {
					nadeAreaPlace = nadeArea.Place.Name
				}
			}		
			grenadeType := e.Base().GrenadeType
			nadeID = e.Base().Grenade.UniqueID()
                        
			fmt.Printf("[GRENADE] [%d] [%d, %f, %f, %s, %s, %s] [%d, %f, %f, %d, %s, %s]\n",
 			    gameTick,
 			    playerID, playerPosXViz, playerPosYViz, playerName, playerSideString, playerAreaPlace,
 			    nadeID, nadePosXViz, nadePosYViz, grenadeType, "explosion", nadeAreaPlace)
		}
    })
    
    p.RegisterEventHandler(func(e events.SmokeStart) {
    	// Flash explodes

		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup grenade events
		if (warmup == false) && (roundStarted == 1) {
			gameTick := p.GameState().IngameTick()
    	    
    	    // Second block (player info)
    	    var playerID uint64 = 0
			var playerPosXViz float64 = 0.0
			var playerPosYViz float64 = 0.0
			var playerName string = "NA"
			var playerSideString string = "NA"
			var playerAreaPlace string = "NA"
					
			// Third block (nade info)
			var nadeID int64 = 0
			var nadePosXViz float64 = 0.0
			var nadePosYViz float64 = 0.0
			var nadeAreaPlace string = "NA"	
			
    	    // get player information
    	    if e.Thrower != nil {
    			playerName = e.Thrower.Name
    			playerPosXViz, playerPosYViz = mapMetadata.TranslateScale(e.Thrower.Position().X, e.Thrower.Position().Y)				
				playerPosPoint := gonav.Vector3{X: float32(e.Thrower.Position().X), Y: float32(e.Thrower.Position().Y), Z: float32(e.Thrower.Position().Z)}
				playerArea := mesh.GetNearestArea(playerPosPoint, true)
				
				if playerArea != nil {
					if playerArea.Place != nil {
						playerAreaPlace = playerArea.Place.Name
					}
				}		
				if e.Thrower.Team == 2 {
					playerSideString = "T"
				} else if e.Thrower.Team == 3 {
					playerSideString = "CT"
				}
				playerID = e.Thrower.SteamID64
    	    }

    		// get nade information   	    
    	    nadePosXViz, nadePosYViz = mapMetadata.TranslateScale(e.Base().Position.X, e.Base().Position.Y)
			nadePosPoint := gonav.Vector3{X: float32(e.Base().Position.X), Y: float32(e.Base().Position.Y), Z: float32(e.Base().Position.Z)}
			nadeArea := mesh.GetNearestArea(nadePosPoint, true)
			if nadeArea != nil {
				if nadeArea.Place != nil {
					nadeAreaPlace = nadeArea.Place.Name
				}
			}		
			grenadeType := e.Base().GrenadeType
			nadeID = e.Base().Grenade.UniqueID()
            
			fmt.Printf("[GRENADE] [%d] [%d, %f, %f, %s, %s, %s] [%d, %f, %f, %d, %s, %s]\n",
 			    gameTick,
 			    playerID, playerPosXViz, playerPosYViz, playerName, playerSideString, playerAreaPlace,
 			    nadeID, nadePosXViz, nadePosYViz, grenadeType, "explosion", nadeAreaPlace)
		}
    })
	
	p.RegisterEventHandler(func(e events.SmokeExpired) {
    	// Flash explodes

		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup grenade events
		if (warmup == false) && (roundStarted == 1) {
			gameTick := p.GameState().IngameTick()
    	    
    	    // Second block (player info)
    	    var playerID uint64 = 0
			var playerPosXViz float64 = 0.0
			var playerPosYViz float64 = 0.0
			var playerName string = "NA"
			var playerSideString string = "NA"
			var playerAreaPlace string = "NA"
					
			// Third block (nade info)
			var nadeID int64 = 0
			var nadePosXViz float64 = 0.0
			var nadePosYViz float64 = 0.0
			var nadeAreaPlace string = "NA"	
			
    	    // get player information
    	    if e.Thrower != nil {
    			playerName = e.Thrower.Name
    			playerPosXViz, playerPosYViz = mapMetadata.TranslateScale(e.Thrower.Position().X, e.Thrower.Position().Y)				
				playerPosPoint := gonav.Vector3{X: float32(e.Thrower.Position().X), Y: float32(e.Thrower.Position().Y), Z: float32(e.Thrower.Position().Z)}
				playerArea := mesh.GetNearestArea(playerPosPoint, true)
				
				if playerArea != nil {
					if playerArea.Place != nil {
						playerAreaPlace = playerArea.Place.Name
					}
				}		
				if e.Thrower.Team == 2 {
					playerSideString = "T"
				} else if e.Thrower.Team == 3 {
					playerSideString = "CT"
				}
				playerID = e.Thrower.SteamID64
    	    }

    		// get nade information   	    
    	    nadePosXViz, nadePosYViz = mapMetadata.TranslateScale(e.Base().Position.X, e.Base().Position.Y)
			nadePosPoint := gonav.Vector3{X: float32(e.Base().Position.X), Y: float32(e.Base().Position.Y), Z: float32(e.Base().Position.Z)}
			nadeArea := mesh.GetNearestArea(nadePosPoint, true)
			if nadeArea != nil {
				if nadeArea.Place != nil {
					nadeAreaPlace = nadeArea.Place.Name
				}
			}		
			grenadeType := e.Base().GrenadeType
			nadeID = e.Base().Grenade.UniqueID()

			fmt.Printf("[GRENADE] [%d] [%d, %f, %f, %s, %s, %s] [%d, %f, %f, %d, %s, %s]\n",
 			    gameTick,
 			    playerID, playerPosXViz, playerPosYViz, playerName, playerSideString, playerAreaPlace,
 			    nadeID, nadePosXViz, nadePosYViz, grenadeType, "expired", nadeAreaPlace)
		}
    })
    
	p.RegisterEventHandler(func(e events.GrenadeProjectileThrow) {
    	// if a player throws a nade -> its creats an entity -> event gets triggerd

		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup grenade events
		if (warmup == false) && (roundStarted == 1) {
    	    gameTick := p.GameState().IngameTick()
    	    
    	    // Second block (player info)
    	    var playerID uint64 = 0
			var playerPosXViz float64 = 0.0
			var playerPosYViz float64 = 0.0
			var playerName string = "NA"
			var playerSideString string = "NA"
			var playerAreaPlace string = "NA"
			
			// Third block (nade info)
			var nadeID int64 = 0
			var nadePosXViz float64 = 0.0
			var nadePosYViz float64 = 0.0
			var nadeAreaPlace string = "NA"
			
			
    	    // get player information
    	    if e.Projectile.Thrower != nil {
    			playerName = e.Projectile.Thrower.Name
    			playerPosXViz, playerPosYViz = mapMetadata.TranslateScale(e.Projectile.Thrower.Position().X, e.Projectile.Thrower.Position().Y)				
				playerPosPoint := gonav.Vector3{X: float32(e.Projectile.Thrower.Position().X), Y: float32(e.Projectile.Thrower.Position().Y), Z: float32(e.Projectile.Thrower.Position().Z)}
				playerArea := mesh.GetNearestArea(playerPosPoint, true)
				
				if playerArea != nil {
					if playerArea.Place != nil {
						playerAreaPlace = playerArea.Place.Name
					}
				}		
				if e.Projectile.Thrower.Team == 2 {
					playerSideString = "T"
				} else if e.Projectile.Thrower.Team == 3 {
					playerSideString = "CT"
				}
				playerID = e.Projectile.Thrower.SteamID64
    	    }
    	    
    	    // get nade information   	    
    	    nadePosXViz, nadePosYViz = mapMetadata.TranslateScale(e.Projectile.Trajectory[0].X, e.Projectile.Trajectory[0].Y)
			nadePosPoint := gonav.Vector3{X: float32(e.Projectile.Trajectory[0].X), Y: float32(e.Projectile.Trajectory[0].Y), Z: float32(e.Projectile.Trajectory[0].Z)}
			nadeArea := mesh.GetNearestArea(nadePosPoint, true)
			if nadeArea != nil {
				if nadeArea.Place != nil {
					nadeAreaPlace = nadeArea.Place.Name
				}
			}
    		grenadeType := e.Projectile.WeaponInstance.Type
    		nadeID = e.Projectile.WeaponInstance.UniqueID()
    		
            fmt.Printf("[GRENADE] [%d] [%d, %f, %f, %s, %s, %s] [%d, %f, %f, %d, %s, %s]\n",
 			    gameTick,
 			    playerID, playerPosXViz, playerPosYViz, playerName, playerSideString, playerAreaPlace,
 			    nadeID, nadePosXViz, nadePosYViz, grenadeType, "create", nadeAreaPlace) 
            	
        }
	})
	/*
	p.RegisterEventHandler(func(e events.GrenadeEventIf) {
		// HE explodes, Flash explodes
		// smoke explodes, but also vanish -> track ID to see if detonate or vanish

		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup grenade events
		if (warmup == false) && (roundStarted == 1) {
			// First block (game state)
			gameTick := p.GameState().IngameTick()

			// Second block (player info)
			var playerPosXViz float64 = 0.0
			var playerPosYViz float64 = 0.0
			var playerName string = "NA"
			var playerSideString string = "NA"
			var playerAreaPlace string = "NA"
			
			// Third block (nade info)
			var nadeID int64 = 0
			var nadePosXViz float64 = 0.0
			var nadePosYViz float64 = 0.0
			var nadeAreaPlace string = "NA"

            // get player information
			if e.Base().Thrower != nil {				
				playerName = e.Base().Thrower.Name
    			playerPosXViz, playerPosYViz = mapMetadata.TranslateScale(e.Base().Thrower.Position().X, e.Base().Thrower.Position().Y)				
				playerPosPoint := gonav.Vector3{X: float32(e.Base().Thrower.Position().X), Y: float32(e.Base().Thrower.Position().Y), Z: float32(e.Base().Thrower.Position().Z)}
				playerArea := mesh.GetNearestArea(playerPosPoint, true)
				
				if playerArea != nil {
					if playerArea.Place != nil {
						playerAreaPlace = playerArea.Place.Name
					}
				}		
				if e.Base().Thrower.Team == 2 {
					playerSideString = "T"
				} else if e.Base().Thrower.Team == 3 {
					playerSideString = "CT"
				}				
			}   			
    			
    		// get nade information   	    
    	    nadePosXViz, nadePosYViz = mapMetadata.TranslateScale(e.Base().Position.X, e.Base().Position.Y)
			nadePosPoint := gonav.Vector3{X: float32(e.Base().Position.X), Y: float32(e.Base().Position.Y), Z: float32(e.Base().Position.Z)}
			nadeArea := mesh.GetNearestArea(nadePosPoint, true)
			if nadeArea != nil {
				if nadeArea.Place != nil {
					nadeAreaPlace = nadeArea.Place.Name
				}
			}		
			grenadeType := e.Base().GrenadeType
			nadeID = e.Base().Grenade.UniqueID()
			
 			if grenadeType != 503 {   					
                 fmt.Printf("[GRENADE] [%d] [%f, %f, %s, %s, %s] [%d, %f, %f, %d, %s, %s]\n",
     			    gameTick,
     			    playerPosXViz, playerPosYViz, playerName, playerSideString, playerAreaPlace,
     			    nadeID, nadePosXViz, nadePosYViz, grenadeType, "explosion", nadeAreaPlace) 
 			}
		}
	})*/

	p.RegisterEventHandler(func(e events.GrenadeProjectileDestroy) {
		// gets triggered if an Entitiy gets destroyed --> nade doesnt exist anymore
		// HE, Flash explosion is events.GrenadeEventIf
		// Smoke explosion and vanish is events.GrenadeEventIf

		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup grenade events
		if (warmup == false) && (roundStarted == 1) {
			// First block (game state)
			gameTick := p.GameState().IngameTick()

			// Second block (player info)
			var playerID uint64 = 0
			var playerPosXViz float64 = 0.0
			var playerPosYViz float64 = 0.0
			var playerName string = "NA"
			var playerSideString string = "NA"
			var playerAreaPlace string = "NA"
			
			// Third block (nade info)
			var nadeID int64 = 0
			var nadePosXViz float64 = 0.0
			var nadePosYViz float64 = 0.0
			var nadeAreaPlace string = "NA"

            // get player information
			if e.Projectile.Thrower != nil {			
				playerName = e.Projectile.Thrower.Name
    			playerPosXViz, playerPosYViz = mapMetadata.TranslateScale(e.Projectile.Thrower.Position().X, e.Projectile.Thrower.Position().Y)				
				playerPosPoint := gonav.Vector3{X: float32(e.Projectile.Thrower.Position().X), Y: float32(e.Projectile.Thrower.Position().Y), Z: float32(e.Projectile.Thrower.Position().Z)}
				playerArea := mesh.GetNearestArea(playerPosPoint, true)
				
				if playerArea != nil {
					if playerArea.Place != nil {
						playerAreaPlace = playerArea.Place.Name
					}
				}		
				if e.Projectile.Thrower.Team == 2 {
					playerSideString = "T"
				} else if e.Projectile.Thrower.Team == 3 {
					playerSideString = "CT"
				}	
				playerID = e.Projectile.Thrower.SteamID64		
			}
				
			// get nade information   	    
    	    nadePosXViz, nadePosYViz = mapMetadata.TranslateScale(e.Projectile.Position().X, e.Projectile.Position().Y)
			nadePosPoint := gonav.Vector3{X: float32(e.Projectile.Position().X), Y: float32(e.Projectile.Position().Y), Z: float32(e.Projectile.Position().Z)}
			nadeArea := mesh.GetNearestArea(nadePosPoint, true)
			if nadeArea != nil {
				if nadeArea.Place != nil {
					nadeAreaPlace = nadeArea.Place.Name
				}
			}		
			grenadeType := e.Projectile.WeaponInstance.Type
            nadeID = e.Projectile.WeaponInstance.UniqueID() 		
 			if (grenadeType == 503) || (grenadeType == 502) {   					
                 fmt.Printf("[GRENADE] [%d] [%d, %f, %f, %s, %s, %s] [%d, %f, %f, %d, %s, %s]\n",
     			    gameTick,
     			    playerID, playerPosXViz, playerPosYViz, playerName, playerSideString, playerAreaPlace,
     			    nadeID, nadePosXViz, nadePosYViz, grenadeType, "destroy", nadeAreaPlace) 
 			}
		}
	})
    
    p.RegisterEventHandler(func(e events.PlayerFlashed) {
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup grenade events
		if (warmup == false) && (roundStarted == 1) {
    		var attackerID uint64 = 0
    		var attackerXViz float64 = 0.0
			var attackerYViz float64 = 0.0
			var attackerSideString string = "NA"
			
			var victimID uint64 = 0
			var victimXViz float64 = 0.0
			var victimYViz float64 = 0.0
			var victimSideString string = "NA"
			
			gameTick := p.GameState().IngameTick()

            // get attacker information
			if e.Attacker != nil {
     			attackerXViz, attackerYViz = mapMetadata.TranslateScale(e.Attacker.Position().X, e.Attacker.Position().Y)

         		if e.Attacker.Team == 2 {
     				attackerSideString = "T"
     			} else if e.Attacker.Team == 3 {
     				attackerSideString = "CT"
     			}
     			attackerID = e.Attacker.SteamID64
            }
            
            // get victim information
            if e.Player != nil {
                victimXViz, victimYViz = mapMetadata.TranslateScale(e.Player.Position().X, e.Player.Position().Y)
    
                 if e.Player.Team == 2 {
     				victimSideString = "T"
     			} else if e.Player.Team == 3 {
     				victimSideString = "CT"
     			}
     			victimID = e.Player.SteamID64
			}
			
			// did the attacker flash an enemy?
			if e.Attacker.Team != e.Player.Team {
    			
    			// we need to iterate over all playing players because observer and GOTV can be flashed aswell...
    			// we get playing Players in event roundstart
    			for _, value := range p.GameState().Participants().Playing() {
    			
        			// lets check if the player who got flashed, is not an spectator and is still alive
                    if (value.Name == e.Player.Name) &&(e.Player.IsAlive())  {
             			fmt.Printf("[ENEMIESFLASHED] [%d] [%d, %f, %f, %s, %s] [%d, %f, %f, %s, %s] \n",
            				gameTick,
            				attackerID, attackerXViz, attackerYViz, e.Attacker.Name, attackerSideString,
            				victimID, victimXViz, victimYViz, e.Player.Name, victimSideString)
                	}
                }
    		}
    		
    		// was it a teamflash?
    		if e.Attacker.Team == e.Player.Team {
        		// we need to iterate over all playing players because observer and GOTV can be flashed aswell...
    			for _, value := range p.GameState().Participants().Playing() {
    			
        			// lets check if the player who got flashed, is not an spectator and is still alive
                    if (value.Name == e.Player.Name) &&(e.Player.IsAlive())  {
            			fmt.Printf("[TEAMFLASHED] [%d] [%d, %f, %f, %s, %s] [%d, %f, %f, %s, %s] \n",
            				gameTick,
            				attackerID, attackerXViz, attackerYViz, e.Attacker.Name, attackerSideString,
            				victimID, victimXViz, victimYViz, e.Player.Name, victimSideString)
                	}
                }
    		}
		}
	})
    
	p.RegisterEventHandler(func(e events.Kill) {
		// Parse player kill events
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup kill events
		if (warmup == false) && (roundStarted == 1) {
			// First block (game state)
			gameTick := p.GameState().IngameTick()

			// Second block (victim location)
			var victimX float64 = 0.0
			var victimY float64 = 0.0
			var victimZ float64 = 0.0
			var VictimXViz float64 = 0.0
			var VictimYViz float64 = 0.0
			var VictimClosestAreaName string = "NA"
			var VictimViewX float32 = 0.0
			var VictimViewY float32 = 0.0

			// Third block (attacker location)
			var attackerX float64 = 0.0
			var attackerY float64 = 0.0
			var attackerZ float64 = 0.0
			var attackerXViz float64 = 0.0
			var attackerYViz float64 = 0.0
			var attackerAssistX float64 = 0.0
			var attackerAssistY float64 = 0.0
    		var attackerAssistZ float64 = 0.0
			var attackerAssistXViz float64 = 0.0
			var attackerAssistYViz float64 = 0.0
			var attackerClosestAreaName string = "NA"
			var attackerViewX float32 = 0.0
			var attackerViewY float32 = 0.0
			var attackerAssistViewX float32 = 0.0
			var attackerAssistViewY float32 = 0.0
			var attackerAssistClosestAreaName string = "NA"

			// Fourth block (victim player/team)
			var victimID uint64 = 0
			var victimName string = "NA"
			var victimSideString string = "NA"

			// Fifth block (attacker player/team)
			var attackerID uint64 = 0
			var attackerName string = "NA"
			var attackerSideString string = "NA"

			var attackerAssistID uint64 = 0
			var attackerAssistName string = "NA"
			var attackerAssistSideString string = "NA"

			// Sixth block (weapon/wallshot/headshot)
			weaponID := e.Weapon.Type
			isWallshot := e.PenetratedObjects
			isHeadshot := e.IsHeadshot
			var isFlashed bool = false

			// Find victim values
			if e.Victim == nil {
				victimID = 0
			} else {
				isFlashed = e.Victim.IsBlinded()

				victimID = e.Victim.SteamID64
				victimX = e.Victim.Position().X
				victimY = e.Victim.Position().Y
				victimZ = e.Victim.Position().Z
				VictimXViz, VictimYViz = mapMetadata.TranslateScale(victimX, victimY)
				VictimViewX = e.Victim.ViewDirectionX()
				VictimViewY = e.Victim.ViewDirectionY()
				victimLoc := gonav.Vector3{X: float32(victimX), Y: float32(victimY), Z: float32(victimZ)}
				victimArea := mesh.GetNearestArea(victimLoc, true)
				if victimArea != nil {
					if victimArea.Place != nil {
						VictimClosestAreaName = victimArea.Place.Name
					}
				}
				victimName = e.Victim.Name
				if e.Victim.Team == 2 {
					victimSideString = "T"
				} else if e.Victim.Team == 3 {
					victimSideString = "CT"
				}
			}

			// Find attacker values
			if e.Killer == nil {
				attackerID = 0
			} else {
				attackerID = e.Killer.SteamID64
				attackerX = e.Killer.Position().X
				attackerY = e.Killer.Position().Y
				attackerZ = e.Killer.Position().Z
				attackerXViz, attackerYViz = mapMetadata.TranslateScale(attackerX, attackerY)
				attackerViewX = e.Killer.ViewDirectionX()
				attackerViewY = e.Killer.ViewDirectionY()
				attackerLoc := gonav.Vector3{X: float32(attackerX), Y: float32(attackerY), Z: float32(attackerZ)}
				attackerArea := mesh.GetNearestArea(attackerLoc, true)
				if attackerArea != nil {
					if attackerArea.Place != nil {
						attackerClosestAreaName = attackerArea.Place.Name
					}
				}
				attackerName = e.Killer.Name
				if e.Killer.Team == 2 {
					attackerSideString = "T"
				} else if e.Killer.Team == 3 {
					attackerSideString = "CT"
				}
			}

			// Find assister values
			if e.Assister == nil {
				attackerAssistID = 0
			} else {
				attackerAssistID = e.Assister.SteamID64
				attackerAssistName = e.Assister.Name
				attackerAssistX = e.Assister.Position().X
				attackerAssistY = e.Assister.Position().Y
				attackerAssistZ = e.Assister.Position().Z
				attackerAssistXViz, attackerAssistYViz = mapMetadata.TranslateScale(attackerX, attackerY)
				attackerAssistViewX = e.Assister.ViewDirectionX()
				attackerAssistViewY = e.Assister.ViewDirectionY()
				attackerAssistLoc := gonav.Vector3{X: float32(attackerAssistX), Y: float32(attackerAssistY), Z: float32(attackerAssistZ)}
				attackerAssistArea := mesh.GetNearestArea(attackerAssistLoc, true)
				if attackerAssistArea != nil {
					if attackerAssistArea.Place != nil {
						attackerAssistClosestAreaName = attackerAssistArea.Place.Name
					}
				}
				if e.Assister.Team == 2 {
					attackerAssistSideString = "T"
				} else {
					attackerAssistSideString = "CT"
				}
			}

			// Print a line of the kill information
			fmt.Printf("[KILL] [%d] [%f, %f, %f, %f, %s] [%f, %f, %f, %f, %s] [%f, %f, %f, %f, %s] [%d, %s, %s] [%d, %s, %s] [%d, %s, %s] [%d, %d, %t, %t] \n",
				gameTick,
				VictimXViz, VictimYViz, VictimViewX, VictimViewY, VictimClosestAreaName,
				attackerXViz, attackerYViz, attackerViewX, attackerViewY, attackerClosestAreaName,
				attackerAssistXViz, attackerAssistYViz, attackerAssistViewX, attackerAssistViewY, attackerAssistClosestAreaName,
				victimID, victimName, victimSideString,
				attackerID, attackerName, attackerSideString,
				attackerAssistID, attackerAssistName, attackerAssistSideString,
				weaponID, isWallshot, isFlashed, isHeadshot)
		}
	})
	
	p.RegisterEventHandler(func(e events.BombPlanted) {
		// Parse bomb plant events
		 
		gs := p.GameState()
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup events
		if (warmup == false) && (roundStarted == 1) {
    		var playerXViz float64 = 0.0
			var playerYViz float64 = 0.0
			var playerID uint64 = 0
			var playerName string = "NA"
			var bombSite = "None"

			playerID = e.BombEvent.Player.SteamID64
			playerName = e.BombEvent.Player.Name
			playerXViz, playerYViz = mapMetadata.TranslateScale(e.BombEvent.Player.Position().X, e.BombEvent.Player.Position().Y)

			if e.Site == 65 {
				bombSite = "A"
			} else if e.Site == 66 {
				bombSite = "B"
			}
			fmt.Printf("[BOMB] [%d] [%f, %f, %d, %s, %s, %s] \n",
				gs.IngameTick(),
				playerXViz, playerYViz, playerID, playerName, bombSite, "plant")
		}
	})

    p.RegisterEventHandler(func(e events.BombExplode) {
		// Parse bomb explode events

		gs := p.GameState()
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup events
		if (warmup == false) && (roundStarted == 1) {
			var playerXViz float64 = 0.0
			var playerYViz float64 = 0.0
			var playerID uint64 = 0
			var playerName string = "NA"
			var bombSite = "None"

			playerID = e.BombEvent.Player.SteamID64
			playerName = e.BombEvent.Player.Name
			playerXViz, playerYViz = mapMetadata.TranslateScale(e.BombEvent.Player.Position().X, e.BombEvent.Player.Position().Y)

			if e.Site == 65 {
				bombSite = "A"
			} else if e.Site == 66 {
				bombSite = "B"
			}
			fmt.Printf("[BOMB] [%d] [%f, %f, %d, %s, %s, %s] \n",
				gs.IngameTick(),
				playerXViz, playerYViz, playerID, playerName, bombSite, "explode")
		}
	})
	
    p.RegisterEventHandler(func(e events.BombDefused) {
		// Parse bomb defuse events
		 
		gs := p.GameState()
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup events
		if (warmup == false) && (roundStarted == 1) {
			var playerXViz float64 = 0.0
			var playerYViz float64 = 0.0
			var playerID uint64 = 0
			var playerName string = "NA"
			var bombSite = "None"

			playerID = e.BombEvent.Player.SteamID64
			playerName = e.BombEvent.Player.Name
			playerXViz, playerYViz = mapMetadata.TranslateScale(e.BombEvent.Player.Position().X, e.BombEvent.Player.Position().Y)

			if e.Site == 65 {
				bombSite = "A"
			} else if e.Site == 66 {
				bombSite = "B"
			}
			fmt.Printf("[BOMB] [%d] [%f, %f, %d, %s, %s, %s] \n",
				gs.IngameTick(),
				playerXViz, playerYViz, playerID, playerName, bombSite, "defuse")
		}
	})
	
	p.RegisterEventHandler(func(e events.BombPickup) {
		// Parse bomb defuse events
		 
		gs := p.GameState()
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup events
		if (warmup == false) && (roundStarted == 1) {
			var playerXViz float64 = 0.0
			var playerYViz float64 = 0.0
			var playerID uint64 = 0
			var playerName string = "NA"
			var bombSite = "NA"

			playerID = e.Player.SteamID64
			playerName = e.Player.Name
			playerXViz, playerYViz = mapMetadata.TranslateScale(e.Player.Position().X, e.Player.Position().Y)

			fmt.Printf("[BOMB] [%d] [%f, %f, %d, %s, %s, %s] \n",
				gs.IngameTick(),
				playerXViz, playerYViz, playerID, playerName, bombSite, "pickup")
		}
	})
	
	p.RegisterEventHandler(func(e events.BombDropped) {
		// Parse bomb defuse events
		 
		gs := p.GameState()
		warmup := p.GameState().IsWarmupPeriod()

		// Only parse non-warmup events
		if (warmup == false) && (roundStarted == 1) {
			var playerXViz float64 = 0.0
			var playerYViz float64 = 0.0
			var playerID uint64 = 0
			var playerName string = "NA"
			var bombSite = "NA"

			playerID = e.Player.SteamID64
			playerName = e.Player.Name
			playerXViz, playerYViz = mapMetadata.TranslateScale(e.Player.Position().X, e.Player.Position().Y)

			fmt.Printf("[BOMB] [%d] [%f, %f, %d, %s, %s, %s] \n",
				gs.IngameTick(),
				playerXViz, playerYViz, playerID, playerName, bombSite, "drop")
		}
	})

    /* 
    p.RegisterEventHandler(func(e events.ItemPickup) {
		// Parse match start events
		warmup := p.GameState().IsWarmupPeriod()
        
		// Only parse non-warmup match starts
		if (warmup == false) && (roundStarted == 1) {
    		// First block (game state)
			gameTick := p.GameState().IngameTick()
			var mapName string = header.MapName
			
            // Second block (Player location)
            var PlayerX float64 = 0.0
 			var PlayerY float64 = 0.0
 			var PlayerZ float64 = 0.0
 			var PlayerXViz float64 = 0.0
 			var PlayerYViz float64 = 0.0
 			var PlayerClosestAreaID uint32 = 0
 			var PlayerClosestAreaName string = "NA"
 			var PlayerViewX float32 = 0.0
 			var PlayerViewY float32 = 0.0
			
            // Third block (Player information)
			var PlayerID uint64 = 0
			var PlayerName string = "NA"
			var PlayerTeam string = "NA"
			var PlayerSide common.Team
			var PlayerSideString string = "NA"
			
			weaponID := e.Weapon.Type
			
			// Find Player values
			if e.Player == nil {
				PlayerID = 0
			} else {
				PlayerID = e.Player.SteamID64
				PlayerX = e.Player.Position().X
				PlayerY = e.Player.Position().Y
				PlayerZ = e.Player.Position().Z
				PlayerXViz, PlayerYViz = mapMetadata.TranslateScale(PlayerX, PlayerY)
				PlayerViewX = e.Player.ViewDirectionX()
				PlayerViewY = e.Player.ViewDirectionY()
				PlayerLoc := gonav.Vector3{X: float32(PlayerX), Y: float32(PlayerY), Z: float32(PlayerZ)}
				PlayerArea := mesh.GetNearestArea(PlayerLoc, true)
				if PlayerArea != nil {
					PlayerClosestAreaID = PlayerArea.ID
					if PlayerArea.Place != nil {
						PlayerClosestAreaName = PlayerArea.Place.Name
					}
				}
				PlayerName = e.Player.Name
				PlayerTeam = e.Player.TeamState.ClanName()
				PlayerSide = e.Player.Team
				if PlayerSide == 2 {
					PlayerSideString = "T"
				} else if PlayerSide == 3 {
					PlayerSideString = "CT"
				}
			}
			// Print a line of the kill information
			fmt.Printf("[ITEMPICKUP] [%s, %d] [%f, %f, %f, %f, %d, %s] [%d, %s, %s, %s, %d] \n",
				mapName, gameTick,
				PlayerXViz, PlayerYViz, PlayerViewX, PlayerViewY, PlayerClosestAreaID, PlayerClosestAreaName,
				PlayerID, PlayerName, PlayerTeam, PlayerSideString, weaponID)
		}
	})
    */	
	
	// Parse demofile to end
	err = p.ParseToEnd()
	checkError(err)
}

// Function to handle errors
func checkError(err error) {
	if err != nil {
		fmt.Printf("[ERROR] Demo Stream Error %s", err)
	}
}
