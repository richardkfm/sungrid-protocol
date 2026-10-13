## mainmenu.yaml
label-main-menu-title = Main Menu
label-main-menu-tagline = A solarpunk reinterpretation of the classic RTS formula

## ingame-observer.yaml
label-economy-stats-harvesters-header = Collectors
label-economy-stats-derricks-header = Derricks
label-grid-reserve-standings-header = Grid Reserve



## ingame-player.yaml
label-grid-reserve-hud =
    .text = Reserve { $current } / { $target }
    .tooltip = Grid Reserve: { $current } banked of the { $target } target. Your { $banks } Battery Banks can hold { $capacity } Reserve.
label-grid-reserve-hud-lockdown =
    .text = GRID LOCKDOWN — { $seconds }s
    .tooltip = Hold Reserve at target for { $seconds }s more to win via Grid Lockdown.
label-grid-reserve-hud-enemy-lockdown =
    .text = ENEMY LOCKDOWN — { $seconds }s
    .tooltip = { $player } is holding Grid Lockdown. Destroy their Battery Banks to break it. { $seconds }s remaining.
label-grid-reserve-briefing-title = Grid Reserve Enabled
label-grid-reserve-briefing-line1 = Battery Banks now convert Credits into Reserve automatically.
label-grid-reserve-briefing-line2 = Deposits are permanent: that money can never be spent again.
label-grid-reserve-briefing-line3 = Build several Banks and reach the Reserve target to win via Grid Lockdown.
label-grid-reserve-briefing-line4 = Destroying a Bank drains part of its Reserve. Selling one forfeits it entirely.
label-grid-reserve-briefing-line5 = At 50% of target, your Banks are revealed on every enemy's minimap.
button-grid-reserve-briefing-close = Got it
label-sun-cycle-phase =
    .day = Day
    .dusk = Dusk
    .night = Night
    .dawn = Dawn
label-sun-cycle-hud =
    .text = { $phase } — { $next } in { $time } · Energy { $stored } / { $capacity } · { $state }
    .tooltip = Solar output { $solar }%. Battery Banks: { $banks }, storing { $stored } of { $capacity } energy ({ $flow }). Each bank charges from spare power at up to { $charge } a second and gives up to { $discharge } a second when the grid runs short.
    .tooltip-reserve = Solar output { $solar }%. Battery Banks: { $banks }, storing { $stored } of { $capacity } energy ({ $flow }). Each bank charges from spare power at up to { $charge } a second and gives up to { $discharge } a second when the grid runs short. Energy comes first: a bank banks no Reserve while it is charging, and { $percent }% of every bank ({ $protected } energy in all) is kept for energy. Grid Reserve holds { $reserve } in the rest.
label-sun-cycle-hud-state =
    .charging = charging
    .draining = draining
    .full = full
    .empty = empty
    .no-surplus = no spare power
    .blackout = blackout
    .no-banks = no Battery Banks
label-sun-cycle-hud-flow =
    .charging = charging +{ $rate }/s
    .discharging = draining { $rate }/s
    .idle = idle
button-command-bar-force-move =
    .tooltip = Force Move
    .tooltipdesc =
    Selected units will move to the desired location
     - Default activity for the target is suppressed
     - Vehicles will attempt to crush enemies at the target location
     - Drones and helicopters will land at the target location

    Left-click icon then right-click on target.
    Hold <(Alt)> to activate temporarily while commanding units.

button-command-bar-force-attack =
    .tooltip = Force Attack
    .tooltipdesc =
    Selected units will attack the targeted unit or location
     - Default activity for the target is suppressed
     - Allows targeting of own or ally forces
     - Long-range artillery and Surge Rocket Launchers will
       always target the location, ignoring units and buildings

    Left-click icon then right-click on target.
    Hold <(Ctrl)> to activate temporarily while commanding units.

button-command-bar-deploy =
    .tooltip = Deploy
    .tooltipdesc =
    Selected units will perform their default deploy activity
     - MCVs will unpack into a Construction Yard
     - Construction Yards will re-pack into an MCV
     - Transports will unload their passengers
     - Demolition Trucks and Tremor Tanks will self-destruct
     - Minelayers will deploy a mine
     - Drones and aircraft will return to their bay or pad

    Acts immediately on selected units.


button-top-buttons-beacon-tooltip = Place Beacon
button-top-buttons-sell-tooltip = Sell
button-top-buttons-power-tooltip = Power Down
button-top-buttons-repair-tooltip = Repair

button-production-types-building-tooltip = Buildings
button-production-types-defense-tooltip = Defense
button-production-types-infantry-tooltip = Infantry
button-production-types-vehicle-tooltip = Vehicles
button-production-types-aircraft-tooltip = Aircraft
button-production-types-naval-tooltip = Naval

## ingame-debug.yaml
button-debug-panel-power-outage = Power Outage
