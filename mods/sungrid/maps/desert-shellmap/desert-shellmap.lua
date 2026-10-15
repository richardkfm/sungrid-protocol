--[[
   Copyright (c) The OpenRA Developers and Contributors
   This file is part of OpenRA, which is free software. It is made
   available to you under the terms of the GNU General Public License
   as published by the Free Software Foundation, either version 3 of
   the License, or (at your option) any later version. For more
   information, see COPYING.
]]

-- Sungrid Protocol main-menu battle (docs/BACKLOG.md issues #119 and #137).
--
-- Rewritten from Scott_NZ's Red Alert desert shellmap script. The terrain and
-- the camera path are his; the roster is ours. The Consortium ("Allies") holds
-- the southern base behind a line of Grid Defense and Arc Turrets, with SAM
-- sites over its Battery Banks; the Assembly ("Soviets") holds the north-east
-- plateau and the north-west ridge behind Arc Pylons and flak.
--
-- What plays out, on a loop that never runs dry:
--  * Assembly ground waves from seven map edges (Disruptor Troopers and Recon
--    Drones, in varying mixes), each re-sent a little after it is wiped out.
--  * Both sides' barracks and drone buildings producing, up to a cap per side;
--    what the Consortium produces hunts its way north into the valley.
--  * A little armour (issue #139): the Consortium's War Factory builds a tank
--    now and then, and an Assembly tank column with an infantry escort comes
--    in from the north or east - at most two tanks a side, the drones already
--    fill the sky.
--  * Assembly drone raids on the Consortium's Battery Banks - the Grid Reserve
--    Vault raid - which the SAM sites shoot down (issue #120's wrecks).
--  * A Consortium Spy, disguised as a Disruptor Trooper, walking into an
--    Assembly Battery Bank (drains its stored charge - the Sun Cycle, issue
--    #136) or Solar Array (a power outage that darkens the Arc Pylons and the
--    flak); the moment it gets in, Strike Drones fly the blackout raid.
--  * Hauler Drones collecting the Scrap the dead leave behind
--    (SpawnsResourceOnDeath): a salvage run to the last fight, every so often,
--    on top of their own searching. Ore Trucks work the two ore fields.
--  * Assembly structures are rebuilt where they fell (rubble, then the build-up
--    art), so the north never empties; the Consortium's map-placed base is
--    unkillable, as it has been since issue #119.
-- Recon Drones fly the old MiG paths. The tanks are the only stock Red Alert
-- units spawned (issue #139, the owner's call; their sprites are Phase 7).
-- The Sun Cycle itself is forced on and sped up in rules.yaml.

AssemblyWaves =
{
	{ "disr", "disr", "disr", "disr", "sgdro" },
	{ "disr", "disr", "disr", "disr", "disr", "disr" },
	{ "disr", "disr", "disr", "sgdro", "sgdro" }
}
AssemblyBeachWave = { "disr", "disr", "disr", "disr", "disr", "disr", "disr" }

-- The Assembly's armour: one heavy tank with an escort, from the two northern
-- entries the collectors already drive in by.
AssemblyArmorWave = { "3tnk", "disr", "disr", "disr" }
ArmorInterval = DateTime.Seconds(70)

-- Where Assembly units attack-move to, at random: open ground at the
-- Consortium's War Factory, its Battery Banks and its western barracks. Not
-- the Construction Yard's own cell, as until issue #144: a building cell can
-- never be reached, so from most starting points the attack-move ended the
-- moment it began, the idle trigger issued it again every tick, and every
-- trooper the Assembly's barracks produced stood at its rally point for good.
-- Only the edge waves sometimes found a path; the valley stayed nearly empty.
AssaultCells = { CPos.New(85, 80), CPos.New(73, 72), CPos.New(60, 68) }

-- Each side's own drone (issues #84/#101): the Assembly flies Recon Drones
-- from its Drone Bays, the Consortium Strike Drones from its Aerial
-- Fabrication Bays.
ProducedUnitTypes =
{
	{ factory = AlliedBarracks1, types = { "disr" } },
	{ factory = AlliedBarracks2, types = { "disr" } },
	{ factory = AlliedDroneBay1, types = { "sgdrs" } },
	{ factory = AlliedDroneBay2, types = { "sgdrs" } },
	{ factory = AlliedAerialFab, types = { "sgdrs" } },
	{ factory = AlliedWarFactory, types = { "1tnk", "2tnk" }, pause = DateTime.Seconds(45) },
	{ factory = SovietBarracks1, types = { "disr" } },
	{ factory = SovietBarracks2, types = { "disr" } },
	{ factory = SovietBarracks3, types = { "disr" } },
	{ factory = SovietDroneBay1, types = { "sgdro" } },
	{ factory = SovietDroneBay2, types = { "sgdro" } },
	{ factory = SovietDroneBay3, types = { "sgdro" } }
}

-- Most of each type a side fields from the script (production, armour
-- columns); a factory waits while its side is at the cap, so nothing
-- accumulates on a menu left open. Only what the script fielded counts: the
-- map already places 23 Consortium troopers, which used to hold its barracks
-- at the cap for good (issue #139).
ProductionCaps = { disr = 10, sgdro = 4, sgdrs = 4, ["1tnk"] = 2, ["2tnk"] = 2, ["3tnk"] = 2 }
TankTypes = { ["1tnk"] = true, ["2tnk"] = true, ["3tnk"] = true }
Fielded = { }

-- Collectors each side keeps working (replaced if lost).
HaulerMinimum = 2
OreTruckMinimum = 1

-- Footprints (width, height) of every Assembly structure type on the map,
-- for the rebuild check below. A type missing here is not rebuilt.
RebuildFootprints =
{
	fact = { 3, 4 }, proc = { 3, 4 }, apwr = { 3, 3 }, powr = { 2, 3 },
	barr = { 2, 3 }, sgdrn = { 2, 3 }, sgdai = { 2, 3 }, sgshl = { 2, 2 },
	rcyd = { 1, 1 }, sgwnd = { 1, 1 }, sgsns = { 1, 1 }, silo = { 1, 1 },
	arct = { 1, 1 }, tsla = { 1, 1 }, agun = { 1, 1 }
}
RebuildDelay = DateTime.Seconds(40)

-- What the Spy goes for, alternately: a Battery Bank (a Spy empties its stored
-- charge while the Sun Cycle runs) or a Solar Array (a power outage).
SpyTargetTypes = { { "silo" }, { "powr", "apwr" } }
BlackoutRaidTargetTypes = { "tsla", "agun", "silo" }

-- The old MiG flight paths, flown by Recon Drones now.
Recon1Waypoints = { Mig11, Mig12, Mig13, Mig14 }
Recon2Waypoints = { Mig21, Mig22, Mig23, Mig24 }

-- A raid's survivors withdraw after this long: a raid on an unkillable Battery
-- Bank (or one whose anti-air has gone dark) must not hover there for good.
RaidDuration = DateTime.Seconds(45)
RaidCap = 9

-- Where the last Assembly unit fell on the Consortium's side of the valley,
-- for the Haulers' salvage run.
SalvageLine = 45
LastWreck = nil
LastWreckTime = 0
SalvageIndex = 0
SpyRound = 0

-- Tanks share one cap per side; everything else is capped by its own type.
FieldedKey = function(player, unitType)
	return player.InternalName .. ":" .. (TankTypes[unitType] and "tank" or unitType)
end

AtCap = function(player, unitType)
	local cap = ProductionCaps[unitType]
	return cap ~= nil and (Fielded[FieldedKey(player, unitType)] or 0) >= cap
end

CountFielded = function(a)
	local key = FieldedKey(a.Owner, a.Type)
	Fielded[key] = (Fielded[key] or 0) + 1
	Trigger.OnRemovedFromWorld(a, function()
		Fielded[key] = Fielded[key] - 1
	end)
end

BindActorTriggers = function(a)
	if a.Owner == Soviets then
		Trigger.OnKilled(a, function(self)
			if self.Location.Y >= SalvageLine then
				LastWreck = self.Location
				LastWreckTime = DateTime.GameTime
			end
		end)
	end

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
					a.AttackMove(Utils.Random(AssaultCells))
				end
			end)
		end
	end
end

-- Hauler Drones and Ore Trucks: a map-placed Harvester searches for resources
-- on creation, and this keeps it searching between trips. Scrap appears where
-- units die (after SpawnsResourceOnDeath's 30 s hold), i.e. along the
-- Consortium's defence line, which is where the Haulers end up driving - the
-- behaviour the mode is built on.
BindHaulerTriggers = function(a)
	Trigger.OnIdle(a, function(a)
		if a.IsInWorld then
			a.FindResources()
		end
	end)
end

-- The Spy retries a few times if it goes idle (its target fell, or no path),
-- then is retired; whatever ends it, the next one follows.
RunSpy = function(spy)
	SpyRound = SpyRound + 1
	local attempts = 1
	spy.DisguiseAsType("disr", Soviets)
	Trigger.OnRemovedFromWorld(spy, function()
		Trigger.AfterDelay(DateTime.Seconds(45), SendSpy)
	end)
	Trigger.OnIdle(spy, function(s)
		if s.IsInWorld then
			attempts = attempts + 1
			if attempts > 3 then
				s.Destroy()
			else
				InfiltrateNearest(s)
			end
		end
	end)
	InfiltrateNearest(spy)
end

InfiltrateNearest = function(spy)
	local targets = Soviets.GetActorsByTypes(SpyTargetTypes[SpyRound % #SpyTargetTypes + 1])
	local best, bestDistance = nil, nil
	Utils.Do(targets, function(t)
		local dx, dy = t.Location.X - spy.Location.X, t.Location.Y - spy.Location.Y
		local d = dx * dx + dy * dy
		if not t.IsDead and (bestDistance == nil or d < bestDistance) then
			best, bestDistance = t, d
		end
	end)

	-- Infiltrate raises an error for a target that has lost its SpyInfiltrate
	-- type (a Battery Bank only carries it while the Sun Cycle runs); retire
	-- the Spy rather than stop the script, and the next one is sent as usual.
	if best == nil or not pcall(function() spy.Infiltrate(best) end) then
		spy.Destroy()
	end
end

SendSpy = function()
	local barracks = SpyRound % 2 == 0 and AlliedBarracks1 or AlliedBarracks2
	if barracks.IsDead then
		barracks = AlliedBarracks1
	end

	barracks.Produce("spy")
end

BindSpyTargets = function(a)
	Trigger.OnInfiltrated(a, function(self, infiltrator)
		if infiltrator.Owner == Allies then
			Trigger.AfterDelay(DateTime.Seconds(2), SendBlackoutRaid)
		end
	end)
end

SendRaid = function(owner, droneType, entry, target)
	local drones = Reinforcements.Reinforce(owner, { droneType, droneType, droneType }, { entry.Location }, 10)
	Utils.Do(drones, function(drone)
		BindActorTriggers(drone)
		drone.Attack(target)
	end)

	Trigger.AfterDelay(RaidDuration, function()
		Utils.Do(drones, function(drone)
			if not drone.IsDead then
				drone.Stop()
				drone.Move(entry.Location)
				drone.Destroy()
			end
		end)
	end)
end

-- The Consortium exploits the Spy's work: Strike Drones in from the south.
SendBlackoutRaid = function()
	local targets = Soviets.GetActorsByTypes(BlackoutRaidTargetTypes)
	if #targets > 0 and #Allies.GetActorsByType("sgdrs") < RaidCap then
		SendRaid(Allies, "sgdrs", Chinook1Entry, Utils.Random(targets))
	end
end

-- The Assembly raids the Consortium's Battery Banks - the Grid Reserve Vault -
-- and the SAM sites over them answer.
SendDroneRaid = function()
	local banks = Allies.GetActorsByType("silo")
	if #banks > 0 and #Soviets.GetActorsByType("sgdro") < RaidCap then
		SendRaid(Soviets, "sgdro", Entry4, Utils.Random(banks))
	end

	Trigger.AfterDelay(DateTime.Seconds(55), SendDroneRaid)
end

-- A Hauler drives out to where the last fight was and collects what it left.
SendSalvageRun = function()
	local haulers = Allies.GetActorsByType("sghau")
	if LastWreck ~= nil and #haulers > 0 and DateTime.GameTime - LastWreckTime >= DateTime.Seconds(31) then
		SalvageIndex = SalvageIndex % #haulers + 1
		local hauler = haulers[SalvageIndex]
		hauler.Stop()
		hauler.Move(LastWreck, 2)
		hauler.FindResources()
		LastWreck = nil
	end

	Trigger.AfterDelay(DateTime.Seconds(40), SendSalvageRun)
end

KeepCollectors = function()
	if #Allies.GetActorsByType("sghau") < HaulerMinimum and not AlliedWarFactory.IsDead then
		AlliedWarFactory.Produce("sghau")
	end

	if #Allies.GetActorsByType("harv") < OreTruckMinimum and not AlliedWarFactory.IsDead then
		AlliedWarFactory.Produce("harv")
	end

	if #Soviets.GetActorsByType("sghau") < HaulerMinimum then
		ReinforceCollector("sghau", Entry5)
	end

	if #Soviets.GetActorsByType("harv") < OreTruckMinimum then
		ReinforceCollector("harv", Entry4)
	end

	Trigger.AfterDelay(DateTime.Seconds(30), KeepCollectors)
end

ReinforceCollector = function(unitType, entry)
	local collectors = Reinforcements.Reinforce(Soviets, { unitType }, { entry.Location }, 0)
	Utils.Do(collectors, function(c)
		BindHaulerTriggers(c)
		c.FindResources()
	end)
end

SendAssemblyUnits = function(entryCell, waves)
	local units = Reinforcements.Reinforce(Soviets, Utils.Random(waves), { entryCell }, 50)
	Utils.Do(units, function(unit)
		BindActorTriggers(unit)
	end)
	Trigger.OnAllKilled(units, function()
		Trigger.AfterDelay(DateTime.Seconds(Utils.RandomInteger(3, 10)), function()
			SendAssemblyUnits(entryCell, waves)
		end)
	end)
end

-- A tank column from the north or the east, alternately, while the Assembly
-- has fewer tanks out than its cap.
ArmorRound = 0
SendAssemblyArmor = function()
	if not AtCap(Soviets, "3tnk") then
		ArmorRound = ArmorRound + 1
		local entry = ArmorRound % 2 == 0 and Entry4 or Entry5
		local units = Reinforcements.Reinforce(Soviets, AssemblyArmorWave, { entry.Location }, 25)
		Utils.Do(units, function(unit)
			if TankTypes[unit.Type] then
				CountFielded(unit)
			end
			BindActorTriggers(unit)
		end)
	end

	Trigger.AfterDelay(ArmorInterval, SendAssemblyArmor)
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

-- A production loop belongs to one factory actor (t.gen); a rebuilt factory
-- starts a new one and the old loop ends instead of running twice.
ProduceUnits = function(t, gen)
	local factory = t.factory
	if gen ~= t.gen or factory.IsDead then
		return
	end

	local unitType = Utils.Random(t.types)
	if AtCap(factory.Owner, unitType) then
		Trigger.AfterDelay(DateTime.Seconds(5), function() ProduceUnits(t, gen) end)
		return
	end

	factory.Wait(Actor.BuildTime(unitType) + (t.pause or 0))
	factory.Produce(unitType)
	factory.CallFunc(function() ProduceUnits(t, gen) end)
end

OnProduced = function(_, a)
	if a.Type == "spy" then
		RunSpy(a)
	elseif a.Type == "sghau" or a.Type == "harv" then
		BindHaulerTriggers(a)
		a.FindResources()
	else
		CountFielded(a)
		BindActorTriggers(a)
	end
end

StartProduction = function(t)
	t.gen = (t.gen or 0) + 1
	Trigger.OnProduction(t.factory, OnProduced)
	ProduceUnits(t, t.gen)
end

-- An Assembly structure that falls is put back where it stood once its cell
-- is clear: units in the way are scattered and the check repeats.
BindRebuild = function(a)
	local footprint = RebuildFootprints[a.Type]
	if footprint == nil then
		return
	end

	local actorType, cell = a.Type, a.Location
	Trigger.OnKilled(a, function()
		Trigger.AfterDelay(RebuildDelay, function() Rebuild(actorType, cell, footprint) end)
	end)
end

Rebuild = function(actorType, cell, footprint)
	local topLeft = Map.CenterOfCell(cell) - WVec.New(512, 512, 0)
	local bottomRight = Map.CenterOfCell(cell + CVec.New(footprint[1] - 1, footprint[2] - 1)) + WVec.New(512, 512, 0)
	local blockers = Map.ActorsInBox(topLeft, bottomRight, function(u)
		return not u.IsDead and u.HasProperty("Scatter")
	end)

	if #blockers > 0 then
		Utils.Do(blockers, function(u) u.Scatter() end)
		Trigger.AfterDelay(DateTime.Seconds(3), function() Rebuild(actorType, cell, footprint) end)
		return
	end

	-- No free Ore Truck or Hauler with a rebuilt Refinery or Depot:
	-- KeepCollectors decides whether one is missing.
	local inits = { Owner = Soviets, Location = cell }
	if actorType == "proc" or actorType == "rcyd" then
		inits.FreeActor = false
	end

	local building = Actor.Create(actorType, true, inits)
	SetupAssemblyStructure(building)
	Utils.Do(ProducedUnitTypes, function(t)
		if t.cell.X == cell.X and t.cell.Y == cell.Y then
			t.factory = building
			StartProduction(t)
		end
	end)
end

SetupAssemblyStructure = function(a)
	BindRebuild(a)
	if a.Type == "silo" or a.Type == "powr" or a.Type == "apwr" then
		BindSpyTargets(a)
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

SetupAssembly = function()
	Utils.Do(Map.NamedActors, function(a)
		if a.Owner == Soviets then
			SetupAssemblyStructure(a)
		end
	end)
end

SetupCollectors = function()
	Utils.Do(Map.ActorsInWorld, function(a)
		if a.Type == "sghau" or a.Type == "harv" then
			BindHaulerTriggers(a)
			a.FindResources()
		end
	end)
end

WorldLoaded = function()
	Allies = Player.GetPlayer("Allies")
	Soviets = Player.GetPlayer("Soviets")

	SetupConsortiumUnits()
	SetupAssembly()
	SetupCollectors()
	Utils.Do(ProducedUnitTypes, function(t)
		t.cell = t.factory.Location
		StartProduction(t)
	end)

	Trigger.AfterDelay(DateTime.Seconds(30), function() SendRecon(Recon1Waypoints) end)
	Trigger.AfterDelay(DateTime.Seconds(30), function() SendRecon(Recon2Waypoints) end)
	Trigger.AfterDelay(DateTime.Seconds(25), SendDroneRaid)
	Trigger.AfterDelay(DateTime.Seconds(20), SendSpy)
	Trigger.AfterDelay(DateTime.Seconds(40), SendSalvageRun)
	Trigger.AfterDelay(DateTime.Seconds(10), KeepCollectors)
	Trigger.AfterDelay(DateTime.Seconds(35), SendAssemblyArmor)

	SendAssemblyUnits(Entry1.Location, AssemblyWaves)
	SendAssemblyUnits(Entry2.Location, AssemblyWaves)
	SendAssemblyUnits(Entry3.Location, AssemblyWaves)
	SendAssemblyUnits(Entry4.Location, AssemblyWaves)
	SendAssemblyUnits(Entry5.Location, AssemblyWaves)
	SendAssemblyUnits(Entry6.Location, AssemblyWaves)
	SendAssemblyUnits(Entry7.Location, { AssemblyBeachWave })
end
