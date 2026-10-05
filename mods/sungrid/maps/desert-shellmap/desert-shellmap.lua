--[[
   Copyright (c) The OpenRA Developers and Contributors
   This file is part of OpenRA, which is free software. It is made
   available to you under the terms of the GNU General Public License
   as published by the Free Software Foundation, either version 3 of
   the License, or (at your option) any later version. For more
   information, see COPYING.
]]

-- Sungrid Protocol main-menu battle (docs/BACKLOG.md issue #119).
--
-- Rewritten from Scott_NZ's Red Alert desert shellmap script. The terrain and
-- the camera path are his; the roster is ours. The Consortium ("Allies") holds
-- the southern base behind a line of Grid Defense and Arc Turrets; the
-- Assembly ("Soviets") probes it with Disruptor Troopers on foot and Strike
-- Drones from its bays, Recon Drones sweep the valley, and Hauler Drones from
-- both Recycling Depots run out to collect the Scrap the fighting leaves
-- behind (SpawnsResourceOnDeath). No stock Red Alert unit is spawned: the
-- MiGs, Chinooks, LST landings, paradrops, tank columns and the Chronosphere
-- of the original script are gone, so nothing on the menu's moving background
-- is art this mod hasn't drawn.

AssemblyWaveTypes = { "disr", "disr", "disr", "sgdrs" }
AssemblyBeachTypes = { "disr", "disr", "disr", "disr", "disr", "disr" }
ConsortiumPatrolTypes = { "disr", "disr" }

ProducedUnitTypes =
{
	{ factory = AlliedBarracks1, types = { "disr" } },
	{ factory = AlliedBarracks2, types = { "disr" } },
	{ factory = SovietBarracks1, types = { "disr" } },
	{ factory = SovietBarracks2, types = { "disr" } },
	{ factory = SovietBarracks3, types = { "disr" } },
	{ factory = AlliedDroneBay1, types = { "sgdrs", "sgdro" } },
	{ factory = AlliedDroneBay2, types = { "sgdrs" } },
	{ factory = SovietDroneBay1, types = { "sgdrs", "sgdrs", "sgdro" } },
	{ factory = SovietDroneBay2, types = { "sgdrs" } },
	{ factory = SovietDroneBay3, types = { "sgdrs", "sgdro" } }
}

-- The old MiG flight paths, flown by unarmed Recon Drones now.
Recon1Waypoints = { Mig11, Mig12, Mig13, Mig14 }
Recon2Waypoints = { Mig21, Mig22, Mig23, Mig24 }

BindActorTriggers = function(a)
	if a.HasProperty("Hunt") then
		if a.Owner == Allies then
			Trigger.OnIdle(a, function(a)
				if a.IsInWorld then
					a.Hunt()
				end
			end)
		else
			Trigger.OnIdle(a, function(a)
				if a.IsInWorld then
					a.AttackMove(AlliedConstructionYard.Location)
				end
			end)
		end
	end
end

-- Hauler Drones: a map-placed Harvester searches for resources on creation, and
-- this keeps it searching between trips. Scrap appears where units die (after
-- SpawnsResourceOnDeath's 30 s hold), i.e. along the Consortium's defence line,
-- which is where the Haulers end up driving - the behaviour the mode is built on.
BindHaulerTriggers = function(a)
	Trigger.OnIdle(a, function(a)
		if a.IsInWorld then
			a.FindResources()
		end
	end)
end

SendAssemblyUnits = function(entryCell, unitTypes, interval)
	local units = Reinforcements.Reinforce(Soviets, unitTypes, { entryCell }, interval)
	Utils.Do(units, function(unit)
		BindActorTriggers(unit)
	end)
	Trigger.OnAllKilled(units, function() SendAssemblyUnits(entryCell, unitTypes, interval) end)
end

SendRecon = function(waypoints)
	local entryPath = { waypoints[1].Location, waypoints[2].Location }
	local drones = Reinforcements.Reinforce(Soviets, { "sgdro" }, entryPath, 4)
	Utils.Do(drones, function(drone)
		drone.Move(waypoints[3].Location)
		drone.Move(waypoints[4].Location)
		drone.Destroy()
	end)

	Trigger.AfterDelay(DateTime.Seconds(40), function() SendRecon(waypoints) end)
end

ProduceUnits = function(t)
	local factory = t.factory
	if not factory.IsDead then
		local unitType = t.types[Utils.RandomInteger(1, #t.types + 1)]
		factory.Wait(Actor.BuildTime(unitType))
		factory.Produce(unitType)
		factory.CallFunc(function() ProduceUnits(t) end)
	end
end

SetupConsortiumUnits = function()
	Utils.Do(Map.NamedActors, function(a)
		if a.Owner == Allies and a.HasProperty("AcceptsCondition") and a.AcceptsCondition("unkillable") then
			a.GrantCondition("unkillable")
			a.Stance = "Defend"
		end
	end)
end

SetupHaulers = function()
	Utils.Do(Map.ActorsInWorld, function(a)
		if a.Type == "sghau" then
			BindHaulerTriggers(a)
			a.FindResources()
		end
	end)
end

SetupFactories = function()
	Utils.Do(ProducedUnitTypes, function(production)
		Trigger.OnProduction(production.factory, function(_, a)
			if a.Type == "sghau" then
				BindHaulerTriggers(a)
			else
				BindActorTriggers(a)
			end
		end)
	end)
end

WorldLoaded = function()
	Allies = Player.GetPlayer("Allies")
	Soviets = Player.GetPlayer("Soviets")

	SetupConsortiumUnits()
	SetupHaulers()
	SetupFactories()
	Utils.Do(ProducedUnitTypes, ProduceUnits)

	Trigger.AfterDelay(DateTime.Seconds(30), function() SendRecon(Recon1Waypoints) end)
	Trigger.AfterDelay(DateTime.Seconds(30), function() SendRecon(Recon2Waypoints) end)

	SendAssemblyUnits(Entry1.Location, AssemblyWaveTypes, 50)
	SendAssemblyUnits(Entry2.Location, AssemblyWaveTypes, 50)
	SendAssemblyUnits(Entry3.Location, AssemblyWaveTypes, 50)
	SendAssemblyUnits(Entry4.Location, AssemblyWaveTypes, 50)
	SendAssemblyUnits(Entry5.Location, AssemblyWaveTypes, 50)
	SendAssemblyUnits(Entry6.Location, AssemblyWaveTypes, 50)
	SendAssemblyUnits(Entry7.Location, AssemblyBeachTypes, 15)
end
