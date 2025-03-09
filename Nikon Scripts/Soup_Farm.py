from Py4GWCoreLib import *
from BotUtilities import *
from WindowUtilites import *

import Items
import Mapping

bot_name = "Nikons Skalefin Soup Farm"

soup_selected = True
soup_exchange = False
soup_input = 250


class Soup_Window(BasicWindow):
    global soup_selected
    
    soup_original_size = [350.0, 400.0]
    soup_explanded_size = [350.0, 475.0]

    def __init__(self, window_name="Basic Window", window_size = [350.0, 470.0], show_logger = True, show_state = True):
        super().__init__(window_name, window_size, show_logger, show_state)

    def ShowMainControls(self):
        if PyImGui.collapsing_header("About - Farm Requirements"):
            PyImGui.begin_child("About_child_window", (0, 235), False, 0)
            PyImGui.text("- Full windwalker, +4 Earth, +1 Scyth, +1 Mysticism")
            PyImGui.text("- Whatever HP rune you can afford and attunement.")
            PyImGui.text("- Suggest Zealous Enchanting Scythe.")
            PyImGui.text("  \t*Droknars Reaper is perfect.")
            PyImGui.text("- Equip Scythe in Slot 2 if not already.")
            PyImGui.text("- Equip Staff in Slot 1 if not already (not required).")
            PyImGui.text(f"- Inventory Snapshot Taken : Current Slots Safe.")
            PyImGui.text(f"- During salvage, saved slots are not touched.")
            PyImGui.text(f"- Moving items you risk losing during sell.")
            PyImGui.text(f"- Just dont move items.")
            PyImGui.text(f"- Will not sell Skalefins, Salv or Id kits.")
            PyImGui.end_child()
        PyImGui.separator()

    def ShowConfigSettingsTabItem(self):
        global soup_selected, soup_input, soup_exchange

        PyImGui.begin_child("MainCollectPanel##Soups", (0.0, 70.0), False, 0)
        if PyImGui.begin_table("Collect_Inputs", 2):
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            soup_selected = PyImGui.checkbox("Farm Skalefin Soup", soup_selected)  
            PyImGui.table_next_column()
            soup_input = PyImGui.input_int("# Skalefins", soup_input) if soup_input >= 0 else 0 
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            soup_exchange = PyImGui.checkbox("Exchange Skalefins", soup_exchange)  
            PyImGui.end_table()
        PyImGui.end_child()
        PyImGui.separator()

        # Base only shows the table with minimum slots in it atm.
        return super().ShowConfigSettingsTabItem()

    def ShowResults(self):
        global soup_input

        PyImGui.separator()
        
        if PyImGui.collapsing_header("Results##Soups", int(PyImGui.TreeNodeFlags.DefaultOpen)):
            if PyImGui.begin_table("Runs_Results", 6):
                soup_data = GetSoupData()
                PyImGui.table_next_row()
                PyImGui.table_next_column()
                PyImGui.text(f"Runs:")
                PyImGui.table_next_column() 
                PyImGui.text(f"{soup_data[0]}")
                PyImGui.table_next_column() 
                PyImGui.text(f"Success: ")
                PyImGui.table_next_column()
                PyImGui.text_colored(f"{soup_data[1]}", (0, 1, 0, 1))
                PyImGui.table_next_column()
                PyImGui.text(f"Fails:")
                PyImGui.table_next_column()
                fails = soup_data[0] - soup_data[1]

                if fails > 0:
                    PyImGui.text_colored(f"{fails}", (1, 0, 0, 1))
                else:
                    PyImGui.text(f"{fails}")

                PyImGui.table_next_row()
                PyImGui.table_next_column()
                PyImGui.text("Soups:")
                PyImGui.table_next_column()
                soup_count = GetSoupCollected()
                if soup_selected and soup_input > 0 and soup_count == 0:            
                    PyImGui.text_colored(f"{soup_count}", (1, 0, 0, 1))
                else:
                    PyImGui.text_colored(f"{soup_count}", (0, 1, 0, 1))
                PyImGui.table_next_column()
                PyImGui.text(f"collected of")
                PyImGui.table_next_column()                
                PyImGui.text(f"{soup_input}")
                PyImGui.table_next_row()
                PyImGui.end_table()

            if PyImGui.begin_table("Run_Times", 2):
                PyImGui.table_next_row()
                PyImGui.table_next_column()
                PyImGui.text(f"Last Run:")
                PyImGui.table_next_column()
                PyImGui.text(f"     {FormatTime(GetRunTime(), "mm:ss:ms")}")
                PyImGui.table_next_row()
                PyImGui.table_next_column()
                PyImGui.text(f"Avg. Run:")
                PyImGui.table_next_column()
                PyImGui.text(f"     {FormatTime(GetAverageRunTime(), "mm:ss:ms")}")
                PyImGui.table_next_row()
                PyImGui.table_next_column()
                PyImGui.text(f"Total:")
                PyImGui.table_next_column()
                PyImGui.text(f"{FormatTime(GetTotalRunTime())}")
                PyImGui.table_next_row()
                PyImGui.end_table()

        PyImGui.separator()

    def ShowBotControls(self):
        if PyImGui.begin_table("Bot_Controls", 4):
            PyImGui.table_next_row()
            PyImGui.table_next_column()

            if not self.IsBotRunning():
                if PyImGui.button("Start"):
                    StartBot()
            else:          
                if PyImGui.button("Stop"):
                    StopBot()     
                
            PyImGui.table_next_column()            
            if PyImGui.button("Reset"):
                ResetBot()  

            PyImGui.table_next_column()            
            if PyImGui.button("Print Saved Slots"):
                PrintData()  

            PyImGui.end_table() 

    def ApplyLootMerchantSettings(self) -> None:
        ApplyLootAndMerchantSelections()

    def ApplyConfigSettings(self) -> None:
        ApplySoupConfigSettings(self.minimum_slots)

    def GetSoupSettings(self):
        global soup_input

        return (soup_input, self.id_Items, self.collect_coins, self.collect_events, self.collect_items_white, self.collect_items_blue, \
                self.collect_items_grape, self.collect_items_gold, self.collect_dye, self.sell_items, self.sell_items_white, \
                self.sell_items_blue, self.sell_items_grape, self.sell_items_gold, self.sell_materials, self.salvage_items, self.salvage_items_white, \
                self.salvage_items_blue, self.salvage_items_grape, self.salvage_items_gold)
                
class Soup_Farm(ReportsProgress):
    class Soup_Skillbar:    
        def __init__(self):
            self.sand_shards = SkillBar.GetSkillIDBySlot(1)
            self.vos = SkillBar.GetSkillIDBySlot(2)
            self.conviction = SkillBar.GetSkillIDBySlot(3)
            self.eremites = SkillBar.GetSkillIDBySlot(4)
            self.drunkMaster = SkillBar.GetSkillIDBySlot(5)
            self.deathsCharge = SkillBar.GetSkillIDBySlot(6)
            self.intimidating = SkillBar.GetSkillIDBySlot(7)
            self.regen = SkillBar.GetSkillIDBySlot(8)

    # soup_Routine is the FSM instance
    soup_Routine = FSM("soup_Main")
    soup_Exchange_Routine = FSM("soup_Exchange")
    inventoryRoutine = InventoryFsm(None, None, 0, None, None)

    soup_Skillbar_Code = "Ogek8Np5Kzmk513GBWzlqIuz+F7F"

    soup_exchange_travel = "Soup- Exchange Travel Astralarium"
    soup_exchange_wait_map = "Soup- Exchange Waiting Map"
    soup_exchange_move_to_collector = "Soup- Exchange Go to Chef"
    soup_exchange_target_collector = "Soup- Exchange Target"
    soup_exchange_interact_collector = "Soup- Exchange Interact"
    soup_exchange_do_exchange_all = "Soup- Exchange Soup"
    soup_exchange_soup_routine_start = "Soup- Go Exchange Soup#1"
    soup_exchange_soup_routine_end = "Soup- Go Exchange Soup#2"
    
    soup_inventory_routine = "DoInventoryRoutine"
    soup_initial_check_inventory = "Soup- Inventory Check"
    soup_check_inventory_after_handle_inventory = "Soup- Inventory Handled?"
    soup_travel_state_name = "Soup- Traveling to Rihlon"
    soup_set_normal_mode = "Soup- Set Normal Mode"
    soup_add_hero_state_name = "Soup- Adding Koss"
    soup_load_skillbar_state_name = "Soup- Load Skillbar"
    soup_pathing_1_state_name = "Soup- Leaving Outpost 1"
    soup_resign_pathing_state_name = "Soup- Setup Resign"
    soup_pathing_2_state_name = "Soup- Leaving Outpost 2"
    soup_waiting_map_state_name = "Soup- Farm Map Loading"
    soup_change_weapon_staff = "Soup- Change to Staff"
    soup_change_weapon_scythe = "Soup- Change to Scythe"
    soup_kill_koss_state_name = "Soup- Killing Koss"
    soup_waiting_run_state_name = "Soup- Move to Farm Spot"
    soup_waiting_kill_state_name = "Soup- Killing Drakes"
    soup_looting_state_name = "Soup- Picking Up Loot"
    soup_resign_state_name = "Soup- Resigning"
    soup_wait_return_state_name = "Soup- Wait Return"
    soup_inventory_state_name = "Soup- Handle Inventory"
    soup_inventory_state_name_end = "Soup-Handle Inventory#2"
    soup_end_state_name = "Soup- End Routine"
    soup_forced_stop = "Soup- End Forced"
    soup_outpost_portal = [(-3102, 1070)] # Used by itself if spawn close to Floodplain portal
    #soup_outpost_pathing = [(-15480, 11138), (-16009, 10219), (-15022, 8470)] # Used when spawn location is near xunlai chest or merchant
    soup_farm_run_pathing = [(-14512, 8238), (-12469, 9387), (-12243, 10163), (-10703, 10952), (-10066, 11265), (-9595, 11343), (-8922, 11625), (-8501, 11756)]
    soup_outpost_resign_pathing = [(20472, 8784)]
    soup_merchant_position = [(1045, 218),(2809, 2026)]
    soup_pathing_portal_only_handler_1 = Routines.Movement.PathHandler(soup_outpost_portal)
    soup_pathing_portal_only_handler_2 = Routines.Movement.PathHandler(soup_outpost_portal)
    soup_pathing_resign_portal_handler = Routines.Movement.PathHandler(soup_outpost_resign_pathing)
    #soup_pathing_move_to_portal_handler = Routines.Movement.PathHandler(soup_outpost_pathing)
    soup_pathing_move_to_kill_handler = Routines.Movement.PathHandler(soup_farm_run_pathing)
    
    soup_exchange_pathing = [(-1545, 2133), (-1638, 3894)]
    soup_exchange_pathing_handler = Routines.Movement.PathHandler(soup_exchange_pathing)
    movement_Handler = Routines.Movement.FollowXY(50)
    
    keep_list = []
    keep_list.extend(Items.IdSalveItems_Array)  #[(Items.Drake_Flesh), (Items.Salve_Kit_Basic), (Items.Salve_Kit_Advanced), (Items.Salve_Kit_Superior), (Items.Id_Kit_Basic), (Items.Id_Kit_Superior)]
    keep_list.extend(Items.EventItems_Array)
    keep_list.append(Items.Skalefin)
    keep_list.append(Items.Dye)
    
    soup_first_after_reset = False
    soup_wait_to_kill = False
    soup_ready_to_kill = False
    soup_killing_conviction_casted = False
    soup_killing_eremites_casted = False
    #soup_sanctity = False
    #soup_intimidating = False

    player_stuck = False
    player_stuck_hos_count = 0
    player_skillbar_load_count = 0
    player_previous_hp = 100

    weapon_slot_staff = 1
    weapon_slot_scythe = 2
    soup_collected = 0
    add_koss_tries = 0
    current_lootable = 0
    current_loot_tries = 0
    current_run_time = 0
    average_run_time = 0
    average_run_history = []
    
    soup_runs = 0
    soup_success = 0
    soup_fails = 0
    
    second_timer_elapsed = 1000
    loot_timer_elapsed = 1500

    skillBar = Soup_Skillbar()
    
    pyParty = PyParty.PyParty()
    pyMerchant = PyMerchant.PyMerchant()
    soup_exchange_timer = Timer()
    soup_second_timer = Timer()
    soup_step_done_timer = Timer()
    soup_stuck_timer = Timer()
    soup_loot_timer = Timer()
    soup_loot_done_timer = Timer()
    soup_stay_alive_timer = Timer()

    current_inventory = []
    stuckPosition = []

    ### --- SETUP --- ###
    def __init__(self, window):
        super().__init__(window)
        self.skillBar = self.Soup_Skillbar()

        self.current_inventory = GetInventoryItemSlots()
        self.inventoryRoutine = InventoryFsm(window, self.soup_inventory_routine, Mapping.Jokanur_Diggings, 
                                             self.soup_merchant_position, self.current_inventory, 
                                             self.keep_list, goldToKeep=5000, logFunc=self.Log)
        
        # Skalefin Exchange Sub Routine
        self.soup_Exchange_Routine.AddState(self.soup_exchange_travel,
                                             execute_fn=lambda: self.ExecuteStep(self.soup_exchange_travel, Routines.Transition.TravelToOutpost(Mapping.Astralarium)),
                                             exit_condition=lambda: Routines.Transition.HasArrivedToOutpost(Mapping.Astralarium),
                                             transition_delay_ms=1000)
        self.soup_Exchange_Routine.AddState(self.soup_exchange_move_to_collector,
                                             execute_fn=lambda: self.ExecuteStep(self.soup_exchange_move_to_collector, Routines.Movement.FollowPath(self.soup_exchange_pathing_handler, self.movement_Handler)),
                                             exit_condition=lambda: Routines.Movement.IsFollowPathFinished(self.soup_exchange_pathing_handler, self.movement_Handler),
                                             run_once=False)
        
        self.soup_Exchange_Routine.AddState(name=self.soup_exchange_target_collector,
                                             execute_fn=lambda: self.ExecuteStep(self.soup_exchange_target_collector, TargetNearestNpc()),
                                             transition_delay_ms=1000)
        
        self.soup_Exchange_Routine.AddState(name=self.soup_exchange_interact_collector,
                                             execute_fn=lambda: self.ExecuteStep(self.soup_exchange_interact_collector, Routines.Targeting.InteractTarget()),
                                             exit_condition=lambda: Routines.Targeting.HasArrivedToTarget())
        
        self.soup_Exchange_Routine.AddState(name=self.soup_exchange_do_exchange_all,
                                             execute_fn=lambda: self.ExecuteStep(self.soup_exchange_do_exchange_all, self.ExchangeSoups()),
                                             exit_condition=lambda: self.ExchangeSoupsDone(), 
                                             run_once=False)
        # Skalefin Exchange Sub Routine
        
        # Soup Farm Main Routine
        self.soup_Routine.AddSubroutine(self.soup_exchange_soup_routine_start,
                       sub_fsm=self.soup_Exchange_Routine,
                       condition_fn=lambda: self.CheckExchangeSoups() and CheckIfInventoryHasItem(Items.Drake_Flesh))        
        self.soup_Routine.AddState(self.soup_travel_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.soup_travel_state_name, Routines.Transition.TravelToOutpost(Mapping.Jokanur_Diggings)),
                       exit_condition=lambda: Routines.Transition.HasArrivedToOutpost(Mapping.Jokanur_Diggings),
                       transition_delay_ms=1000)
        self.soup_Routine.AddState(self.soup_initial_check_inventory, execute_fn=lambda: self.CheckInventory())
        self.soup_Routine.AddState(self.soup_set_normal_mode,
                       execute_fn=lambda: self.ExecuteStep(self.soup_set_normal_mode, Party.SetNormalMode()),
                       transition_delay_ms=1000)
        self.soup_Routine.AddState(self.soup_add_hero_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.soup_add_hero_state_name, Party.LeaveParty()), # Ensure only one hero in party
                       transition_delay_ms=1000)
        self.soup_Routine.AddState(self.soup_load_skillbar_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.soup_load_skillbar_state_name, self.LoadSkillBar()), # Ensure only one hero in party                       
                       exit_condition=lambda: self.IsSkillBarLoaded(),
                       transition_delay_ms=1500)
        self.soup_Routine.AddState(self.soup_pathing_1_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.soup_pathing_1_state_name, Routines.Movement.FollowPath(self.soup_pathing_portal_only_handler_1, self.movement_Handler)),
                       exit_condition=lambda: Routines.Movement.IsFollowPathFinished(self.soup_pathing_portal_only_handler_1, self.movement_Handler) or Map.GetMapID() == Mapping.Fahranur_First_City,
                       run_once=False)
        self.soup_Routine.AddState(self.soup_resign_pathing_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.soup_resign_pathing_state_name, Routines.Movement.FollowPath(self.soup_pathing_resign_portal_handler, self.movement_Handler)),
                       exit_condition=lambda: Map.GetMapID() == Mapping.Rilohn_Refuge and Party.IsPartyLoaded(), # or Routines.Movement.IsFollowPathFinished(soup_pathing_resign_portal_handler, movement_Handler) or Map.GetMapID() == Mapping.Rilohn_Refuge,
                       run_once=False)
        self.soup_Routine.AddSubroutine(self.soup_inventory_state_name,
                       sub_fsm = self.inventoryRoutine, # dont add execute function wrapper here
                       condition_fn=lambda: not self.soup_first_after_reset and Inventory.GetFreeSlotCount() <= self.default_min_slots)        
        self.soup_Routine.AddState(self.soup_check_inventory_after_handle_inventory, execute_fn=lambda: self.CheckInventory())
        self.soup_Routine.AddState(self.soup_change_weapon_staff,
                       execute_fn=lambda: self.ExecuteStep(self.soup_change_weapon_staff, ChangeWeaponSet(self.weapon_slot_staff)),
                       transition_delay_ms=1000)
        self.soup_Routine.AddState(self.soup_pathing_2_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.soup_pathing_2_state_name, Routines.Movement.FollowPath(self.soup_pathing_portal_only_handler_2, self.movement_Handler)),
                       exit_condition=lambda: Routines.Movement.IsFollowPathFinished(self.soup_pathing_portal_only_handler_2, self.movement_Handler) or Map.GetMapID() == Mapping.Fahranur_First_City,
                       run_once=False)
        self.soup_Routine.AddState(self.soup_waiting_map_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.soup_waiting_map_state_name, Routines.Transition.IsExplorableLoaded()),
                       transition_delay_ms=1000)
        self.soup_Routine.AddState(self.soup_waiting_run_state_name,
                       execute_fn=lambda: self.ExecuteTimedStep(self.soup_waiting_run_state_name, self.TimeToRunToDrakes()),
                       exit_condition=lambda: self.RunToDrakesDone(),
                       run_once=False)
        self.soup_Routine.AddState(self.soup_change_weapon_scythe,
                       execute_fn=lambda: self.ExecuteStep(self.soup_change_weapon_scythe, ChangeWeaponSet(self.weapon_slot_scythe)),
                       transition_delay_ms=1000)
        self.soup_Routine.AddState(self.soup_waiting_kill_state_name,
                       execute_fn=lambda: self.ExecuteTimedStep(self.soup_waiting_kill_state_name, self.KillLoopStart()),
                       exit_condition=lambda: self.KillLoopComplete() or self.ShouldForceTransitionStep(),
                       run_once=False)
        self.soup_Routine.AddState(self.soup_looting_state_name,
                       execute_fn=lambda: self.ExecuteTimedStep(self.soup_looting_state_name, self.LootLoopStart()),
                       exit_condition=lambda: self.LootLoopComplete() or self.ShouldForceTransitionStep(),
                       run_once=False)
        self.soup_Routine.AddState(self.soup_resign_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.soup_resign_state_name, Player.SendChatCommand("resign")),
                       exit_condition=lambda: Agent.IsDead(Player.GetAgentID()) or Map.GetMapID() == Mapping.Jokanur_Diggings,
                       transition_delay_ms=3000)
        self.soup_Routine.AddState(self.soup_wait_return_state_name,
                       execute_fn=lambda: self.ExecuteTimedStep(self.soup_wait_return_state_name, Party.ReturnToOutpost()),
                       exit_condition=lambda: Map.GetMapID() == Mapping.Rilohn_Refuge and Party.IsPartyLoaded() or self.ShouldForceTransitionStep(),
                       transition_delay_ms=3000)
        self.soup_Routine.AddState(self.soup_end_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.soup_end_state_name, self.CheckSoupRoutineEnd()),
                       transition_delay_ms=1000)        
        self.soup_Routine.AddSubroutine(self.soup_inventory_state_name_end,
                       sub_fsm = self.inventoryRoutine)       
        self.soup_Routine.AddSubroutine(self.soup_exchange_soup_routine_end,
                       condition_fn=lambda: self.CheckExchangeSoups() and CheckIfInventoryHasItem(Items.Drake_Flesh))
        self.soup_Routine.AddState(self.soup_forced_stop,                                    
                       execute_fn=lambda: self.ExecuteStep(self.soup_forced_stop, None))
        
        self.RunTimer = Timer()
        self.TotalTimer = Timer()

    def CheckExchangeSoups(self):
        global soup_exchange
        self.Log(f"Exchange Skalefins: {soup_exchange}")
        return soup_exchange
    
    # Start the Soup routine from the first state after soft reset in case player moved around.
    def Start(self):
        if self.soup_Routine and not self.soup_Routine.is_started():
            self.SoftReset()
            self.soup_Routine.start()
            self.window.StartBot()

    # Stop the Soup routine.
    def Stop(self):
        if not self.soup_Routine:
            return
        
        self.InternalStop()
        
        if self.soup_Routine.is_started():
            self.soup_Routine.stop()
            self.window.StopBot()

    def InternalStart(self):
        Party.SetNormalMode()
        self.TotalTimer.Start()

    def InternalStop(self):
        self.soup_Routine.jump_to_state_by_name(self.soup_forced_stop)
        self.window.StopBot()
        self.TotalTimer.Stop()
        self.RunTimer.Stop()

    def PrintData(self):
        if self.current_inventory != None:
            totalSlotsFull = 0
            for (bag, slots) in self.current_inventory:
                if isinstance(slots, list):
                    totalSlotsFull += len(slots)
                    for slot in slots:
                        self.Log(f"Bag: {bag}, Slot: {slot}")
            self.Log(f"Total Slots Full: {totalSlotsFull}")

    def Reset(self):     
        if self.soup_Routine:
            #self.soup_Routine.stop()
            #self.soup_Routine.reset()
            self.InternalStop()
        
        self.soup_collected = 0    
        self.soup_runs = 0
        self.soup_success = 0
        self.soup_fails = 0

        self.soup_first_after_reset = True      
        self.average_run_history.clear()
        self.average_run_time = 0
        self.current_run_time = 0   

        self.SoftReset()

        # Get new set of inventory slots to keep around in case player went and did some shit, then came back
        self.window.ResetBot()

    def SoftReset(self):
        self.player_stuck = False
        self.soup_wait_to_kill = False
        self.soup_ready_to_kill = False
        self.soup_killing_conviction_casted = False
        self.soup_killing_eremites_casted = False
        self.step_transition_threshold_timer.Reset()
        
        self.add_koss_tries = 0
        self.player_stuck_hos_count = 0
        self.current_lootable = 0
        self.current_loot_tries = 0

        #soup_Window.soup_id_items, soup_Window.soup_collect_coins, soup_Window.soup_collect_events, soup_Window.soup_collect_items_white, soup_Window.soup_collect_items_blue, \
        #soup_Window.soup_collect_items_grape, soup_Window.soup_collect_items_gold, soup_Window.soup_collect_dye
        
        self.inventoryRoutine.Reset()
        self.inventoryRoutine.ApplySelections(idItems=self.idItems, sellItems=self.sellItems, sellWhites=self.sellWhites, 
                                             sellBlues=self.sellBlues, sellGrapes=self.sellGrapes, sellGolds=self.sellGolds, sellGreens=self.sellGreens, 
                                             sellMaterials=self.sellMaterials, salvageItems=self.salvageItems, salvWhites=self.salvWhites, salvBlue=self.salvBlues,
                                             salvGrapes=self.salvGrapes, salvGolds=self.salvGold)
        self.ResetPathing()

    def ResetPathing(self):        
        self.movement_Handler.reset()
        self.soup_loot_timer.Stop()
        self.soup_loot_done_timer.Stop()
        self.soup_stuck_timer.Stop()
        self.soup_second_timer.Stop()
        self.soup_stay_alive_timer.Stop()
        self.soup_step_done_timer.Stop()
        self.soup_pathing_move_to_kill_handler.reset()
        self.soup_pathing_resign_portal_handler.reset()
        self.soup_pathing_portal_only_handler_1.reset()
        self.soup_pathing_portal_only_handler_2.reset()
        #self.soup_pathing_move_to_portal_handler.reset()

    def IsBotRunning(self):
        return self.soup_Routine.is_started() and not self.soup_Routine.is_finished()

    def Update(self):
        if self.soup_Routine.is_started() and not self.soup_Routine.is_finished():
            self.soup_Routine.update()

    def Resign(self):
        if self.soup_Routine.is_started():
            self.soup_runs += 1
            self.soup_Routine.jump_to_state_by_name(self.soup_resign_state_name)

    def SuccessResign(self):
        self.Resign()
        self.soup_success += 1

    def FailResign(self):
        self.Resign()
        self.soup_fails += 1

    def RunStarting(self):
        self.RunTimer.Reset()

        if not self.TotalTimer.IsRunning():
            self.TotalTimer.Start()

        # starting new run, change to staff if available
        ChangeWeaponSet(self.weapon_slot_staff)

    def RunEnding(self):
        elapsed = self.RunTimer.GetElapsedTime()
        self.RunTimer.Stop()

        self.average_run_history.append(elapsed)

        if len(self.average_run_history) >= 100:
            self.average_run_history.pop(0)

        self.average_run_time = sum(self.average_run_history) / len(self.average_run_history)

    def GetCurrentRunTime(self):
        return self.RunTimer.GetElapsedTime()
    
    def GetAverageTime(self):
        return self.average_run_time
    
    def GetTotalTime(self):
        return self.TotalTimer.GetElapsedTime()
    
    def ExchangeSoups(self):
        if not self.soup_exchange_timer.IsRunning():
            self.soup_exchange_timer.Start()

        if not self.soup_exchange_timer.HasElapsed(40):
            return
        
        self.soup_exchange_timer.Reset()

        try:
            turn_in = GetItemIdFromModelId(Items.Skalefin)

            if turn_in == 0:
                return
            
            items3 = self.pyMerchant.get_merchant_item_list()                
            if items3:
                for item in items3:
                    if Item.GetModelID(item) == Items.Skalefin_Soup:
                        self.pyMerchant.collector_buy_item(item, 0, [turn_in], [1])

        except Exception as e:
            self.Log(f"Error in Exchanging soup: {str(e)}", Py4GW.Console.MessageType.Error)

    def ExchangeSoupsDone(self):
        return not CheckIfInventoryHasItem(Items.Skalefin)
    
    def CheckSurrounded(self):
        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), GameAreas.Earshot)
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')

        return len(enemy_array) > 2 or self.player_stuck
    
    def CheckInventory(self):
        if Inventory.GetFreeSlotCount() <= self.default_min_slots:
            self.Log("Bags Full - Manually Handle")
            self.Stop()

    def Log(self, text, msgType=Py4GW.Console.MessageType.Info):
        if self.window:
            self.window.Log(text, msgType)
    ### --- SETUP --- ###

    ### --- ROUTINE FUNCTIONS --- ###
    def LoadSkillBar(self):
        primary_profession, secondary = Agent.GetProfessionNames(Player.GetAgentID())

        if primary_profession != "Dervish":
            self.Log("Bot Requires Dervish Primary")
            self.InternalStop()  
        elif secondary != "Assassin":
            self.Log("Bot Requires Assassin Secondary")
            self.InternalStop()
        else:
            SkillBar.LoadSkillTemplate(self.soup_Skillbar_Code)
    
    def IsSkillBarLoaded(self):
        primary_profession, secondary = Agent.GetProfessionNames(Player.GetAgentID())
        
        if primary_profession != "Dervish":        
            self.Log("Bot Requires Dervish Primary", Py4GW.Console.MessageType.Error)            
            self.InternalStop()
            return False        
        elif secondary != "Assassin":
            self.Log("Bot Requires Assassin Secondary")
            self.InternalStop()
            return False
        else:
            if SkillBar.GetSkillIDBySlot(1) == 0 or SkillBar.GetSkillIDBySlot(2) == 0 or \
            SkillBar.GetSkillIDBySlot(3) == 0 or SkillBar.GetSkillIDBySlot(4) == 0 or \
            SkillBar.GetSkillIDBySlot(5) == 0 or SkillBar.GetSkillIDBySlot(6) == 0 or \
            SkillBar.GetSkillIDBySlot(7) == 0 or SkillBar.GetSkillIDBySlot(8) == 0:
                self.player_skillbar_load_count += 1
                if self.player_skillbar_load_count > 10:
                    self.Log("Unable to Load Skills")
                    self.InternalStop()
                return False
        
        return True

    def TimeToRunToDrakes(self):
        if not self.soup_second_timer.IsRunning():
            self.soup_second_timer.Start()

        if not self.soup_second_timer.HasElapsed(100):
            return
        
        self.soup_second_timer.Reset()
                      
        try:
            if Agent.IsDead(Player.GetAgentID()):
                self.FailResign()
                return
                
            # Checking whether the player is stuck
            self.HandleStuck()

            # Run the stay alive script.
            self.StayAliveLoop()

            # Try to follow the path based on pathing points and movement handler.
            Routines.Movement.FollowPath(self.soup_pathing_move_to_kill_handler, self.movement_Handler)
        except Exception as e:
            Py4GW.Console.Log("Run To Drakes", str(e), Py4GW.Console.MessageType.Error)

    def RunToDrakesDone(self):
        if not self.soup_step_done_timer.IsRunning():
            self.soup_step_done_timer.Start()

        if not self.soup_step_done_timer.HasElapsed(500):
            return False
        
        self.soup_step_done_timer.Reset()

        pathDone = Routines.Movement.IsFollowPathFinished(self.soup_pathing_move_to_kill_handler, self.movement_Handler)         
        surrounded = self.CheckSurrounded(2)
        forceStep = self.ShouldForceTransitionStep()

        return pathDone or surrounded or forceStep

    def KillLoopStart(self):
        self.StayAliveLoop()
        self.Kill()

    # Stay alive using all heal buffs and hos if available
    def StayAliveLoop(self):
        if not self.soup_stay_alive_timer.IsRunning():
            self.soup_stay_alive_timer.Start()

        if not self.soup_stay_alive_timer.HasElapsed(1000):
            return
        
        self.soup_stay_alive_timer.Reset()

        try:            
            player_id = Player.GetAgentID()

            if Agent.IsDead(player_id):
                self.FailResign()
                return
                
            if not CanCast(player_id):
                return
             
            if self.soup_killing_conviction_casted:
                return


            enemies = AgentArray.GetEnemyArray()
            enemies = AgentArray.Filter.ByDistance(enemies, Player.GetXY(), GameAreas.Spellcast)
            enemies = AgentArray.Filter.ByAttribute(enemies, 'IsAlive')

            if len(enemies) > 0 or self.player_stuck:
                # Cast stay alive spells if needed.
                maxHp = Agent.GetMaxHealth(player_id)                
                hp = Agent.GetHealth(player_id) * maxHp
                dangerHp = .7 * maxHp
                
                # Cast HOS is available but find enemy behind if able, otherwise just use since need to heal.
                if self.player_stuck or hp < dangerHp:
                    if len(enemies) > 0:
                        if not IsEnemyBehind(enemies[0]):
                            for enemy in enemies:
                                if IsEnemyBehind(enemy):
                                    break

                    if HasEnoughEnergy(self.skillBar.deathsCharge) and IsSkillReadyById(self.skillBar.deathsCharge):
                        CastSkillById(self.skillBar.deathsCharge)

                        if self.player_stuck:
                            self.player_stuck_hos_count += 1

                            if self.player_stuck_hos_count > 2:
                                # kill shit then if not already
                                self.soup_ready_to_kill = True
                                self.soup_Routine.jump_to_state_by_name(self.soup_waiting_kill_state_name)
                        return
                    
                regen_time_remain = 0
                intimidate_time_remain = 0
                                  
                player_buffs = Effects.GetEffects(player_id)

                for buff in player_buffs:
                    if buff.skill_id == self.skillBar.regen:
                        regen_time_remain = buff.time_remaining
                    if buff.skill_id == self.skillBar.intimidating:
                        intimidate_time_remain = buff.time_remaining

                if regen_time_remain < 3000 and HasEnoughEnergy(self.skillBar.regen) and IsSkillReadyById(self.skillBar.regen):
                    CastSkillById(self.skillBar.regen)
                    return
                
                hasShards = HasBuff(player_id, self.skillBar.sand_shards)

                if not hasShards and IsSkillReadyById(self.skillBar.sand_shards) and HasEnoughEnergy(self.skillBar.sand_shards) and len(enemies) > 1:
                    CastSkillById(self.skillBar.sand_shards)
                    return
                                 
                # Only cast these when waiting for the killing to start.
                if self.soup_Routine.get_current_step_name() == self.soup_waiting_kill_state_name or hp < dangerHp:
                    if intimidate_time_remain < 3000 and HasEnoughEnergy(self.skillBar.intimidating) and IsSkillReadyById(self.skillBar.intimidating):
                        CastSkillById(self.skillBar.intimidating)
                        return
        except Exception as e:
            Py4GW.Console.Log("StayAlive", str(e), Py4GW.Console.MessageType.Error)

    def Kill(self):
        if not self.soup_second_timer.IsRunning():
            self.soup_second_timer.Start()

        if not self.soup_second_timer.HasElapsed(1000):
            return
        
        self.soup_second_timer.Reset()

        try:  
            # Start waiting to kill routine. 
            player_id = Player.GetAgentID()            

            if Agent.IsDead(player_id):
                self.FailResign()
                return
            
            if not CanCast(player_id):
                return  

            if (Map.IsMapReady() and not Map.IsMapLoading()):
                if (Map.IsExplorable() and Map.GetMapID() == Mapping.Floodplain_Of_Mahnkelon and Party.IsPartyLoaded()):
                    enemies = AgentArray.GetEnemyArray()
                    enemies = AgentArray.Filter.ByDistance(enemies, Player.GetXY(), GameAreas.Nearby)
                    enemies = AgentArray.Filter.ByAttribute(enemies, 'IsAlive')
                                           
                    # Ensure have damage mitigation up before attacking
                    if len(enemies) > 1 and (not HasBuff(player_id, self.skillBar.intimidating) or not HasBuff(player_id, self.skillBar.sanctity)):
                        return
                    
                    target = Player.GetTargetID()

                    if target not in enemies:
                        target = enemies[0]

                    Player.ChangeTarget(target)
                        
                    if self.soup_killing_conviction_casted and IsSkillReadyById(self.skillBar.eremites) and HasEnoughEnergy(self.skillBar.eremites):  
                        self.soup_killing_conviction_casted = False
                        # self.Log("eremites")
                        CastSkillById(self.skillBar.eremites)
                        return                    
                    
                    vos_time_remain = 0

                    # Cast stay alive spells if needed.      
                    player_buffs = Effects.GetEffects(player_id)
                    
                    for buff in player_buffs:
                        if buff.skill_id == self.skillBar.vos:
                            vos_time_remain = buff.time_remaining
                                                
                    hasShards = HasBuff(player_id, self.skillBar.sand_shards)

                    if not self.soup_killing_conviction_casted and not hasShards and IsSkillReadyById(self.skillBar.sand_shards) and HasEnoughEnergy(self.skillBar.sand_shards) and len(enemies) > 1:
                        # self.Log("shards")
                        CastSkillById(self.skillBar.sand_shards)
                        return
                                            
                    # Get Ready for killing
                    # Need find a way to change weapon set since  sending the change keys is not working for F1-F4
                    # For now assume we're good to go.
                    if not self.soup_killing_conviction_casted and vos_time_remain < 3000 and IsSkillReadyById(self.skillBar.vos) and HasEnoughEnergy(self.skillBar.vos):                        
                        # self.Log("vos")
                        CastSkillById(self.skillBar.vos)
                        return
                        
                    if IsSkillReadyById(self.skillBar.eremites) and HasEnoughEnergy(self.skillBar.eremites):
                        if IsSkillReadyById(self.skillBar.conviction) and HasEnoughEnergy(self.skillBar.conviction):
                            self.soup_killing_conviction_casted = True
                            # self.Log("stagger")
                            CastSkillById(self.skillBar.conviction)
                    elif not Agent.IsAttacking(player_id) and not Agent.IsCasting(player_id):
                        # Normal Attack
                        #self.Log("attack")
                        Player.Interact(target)
        except Exception as e:
            Py4GW.Console.Log("Kill Loop Error", f"Kill Loop Error {str(e)}", Py4GW.Console.MessageType.Error)

    def KillLoopComplete(self):
        try:
            if Agent.IsDead(Player.GetAgentID()):
                self.FailResign()
                return False
        
            enemies = AgentArray.GetEnemyArray()
            enemies = AgentArray.Filter.ByDistance(enemies, Player.GetXY(), GameAreas.Lesser_Earshot)
            enemies = AgentArray.Filter.ByAttribute(enemies, 'IsAlive')

            if len(enemies) == 0:
                return True

            return False
        except:
            self.Log("Kill Loop Error", Py4GW.Console.MessageType.Error)

    # If issues comment internals and call super().CanPickUp()
    def CanPickUp(self, agentId):
        # Check if our item is a Soup first, otherwise let base hangle it.
        item = Agent.GetItemAgent(agentId)

        if item:     
            model = Item.GetModelID(item.item_id)

            if model == Items.Skalefin:
                return True
            else:
                return super().CanPickUp(agentId)
              
        return False
    
    def LootLoopStart(self):
        try:
            if not self.soup_loot_timer.IsRunning():
                self.soup_loot_timer.Start()

            if self.soup_loot_timer.HasElapsed(self.loot_timer_elapsed):                
                self.soup_loot_timer.Reset()

                # Check if the current item has been picked up.
                if self.current_lootable != 0:
                    ag = Agent.GetAgentByID(self.current_lootable)
                    test = ag.item_agent.agent_id

                    if test != 0:
                        self.current_loot_tries += 1

                        if self.current_loot_tries > 10:
                            self.Log("Loot- 1000 meters away? Frig it.")
                            self.SuccessResign()
                        return  
                    else:
                        self.current_lootable = 0
                
                item = self.GetNearestPickupItem()

                if item == 0 or item == None:
                    self.current_lootable = 0
                    return                
                
                if self.current_lootable != item:
                    self.current_lootable = item

                model = Item.GetModelID(Agent.GetItemAgent(self.current_lootable).item_id)

                if model == Items.Drake_Flesh:
                    self.soup_collected += 1

                Player.Interact(item)
        except Exception as e:
            Py4GW.Console.Log("Loot Loop", f"Error during looting {str(e)}", Py4GW.Console.MessageType.Error)

    def LootLoopComplete(self):
        try:
            if not self.soup_loot_done_timer.IsRunning():
                self.soup_loot_done_timer.Start()

            if self.soup_loot_done_timer.HasElapsed(self.loot_timer_elapsed):
                self.soup_loot_done_timer.Reset()

                if self.current_lootable == 0 or Inventory.GetFreeSlotCount() == 0:
                    self.soup_runs += 1
                    self.soup_success += 1
                    return True

            return False
        except Exception as e:
            Py4GW.Console.Log("Loot Loop Complete", f"Error during looting {str(e)}", Py4GW.Console.MessageType.Error)
    
    def GetSoupCollected(self):
        return self.soup_collected

    def GetSoupStats(self):
        return (self.soup_runs, self.soup_success)
    
    # Jump back to output pathing if not done collecting
    def CheckSoupRoutineEnd(self):
        # Don't reset the Soup count
        self.RunEnding()
        self.SoftReset()

        self.soup_first_after_reset = False

        if self.soup_collected < self.main_item_collect:
            # mapping to outpost may have failed OR the threshold was reached. Try to map there and start over.
            if Map.GetMapID() != Mapping.Rilohn_Refuge:
                self.soup_Routine.jump_to_state_by_name(self.soup_travel_state_name)
            else:
                # already at outpost, check slot count, handle inv or continue farm
                if Inventory.GetFreeSlotCount() <= self.default_min_slots:
                    self.UpdateState(self.soup_inventory_state_name)
                    self.soup_Routine.jump_to_state_by_name(self.soup_inventory_state_name)
                else:
                    self.soup_Routine.jump_to_state_by_name(self.soup_change_weapon_staff)
        else:
            self.Log("Soup Count Matched - AutoStop")
            self.InternalStop()
    
    def HandleStuck(self):  
        try:
            if (Map.IsExplorable() and Party.IsPartyLoaded()):
                if not self.soup_stuck_timer.IsRunning():
                    self.soup_stuck_timer.Start()

                currentStep = self.soup_Routine.get_current_step_name()

                playerId = Player.GetAgentID()
                localPosition = Player.GetXY()

                if currentStep == self.soup_waiting_run_state_name and self.stuckPosition:                
                    if not Agent.IsCasting(playerId) and not Agent.IsKnockedDown(playerId) and not Agent.IsMoving(playerId) or (abs(localPosition[0] - self.stuckPosition[0]) <= 20 and abs(localPosition[1] - self.stuckPosition[1]) <= 20):
                        if self.soup_stuck_timer.HasElapsed(4000):
                            self.player_stuck = True
                            self.soup_stuck_timer.Reset()
                    else:                    
                        self.soup_stuck_timer.Stop()
                        self.player_stuck = False

                self.stuckPosition = localPosition
            else:
                self.soup_stuck_timer.Stop()
                self.soup_stuck_timer.Reset()
                self.player_stuck = False
        except Exception as e:
            Py4GW.Console.Log("Handle Stuck", f"Error during checking stuck {str(e)}", Py4GW.Console.MessageType.Error)
  
  ### --- ROUTINE FUNCTIONS --- ###

def GetSoupCollected():
    return soup_Routine.GetSoupCollected()

def GetSoupData():
    return soup_Routine.GetSoupStats()

soup_Window = Soup_Window(bot_name)
soup_Routine = Soup_Farm(soup_Window)

def ApplyLootAndMerchantSelections():
    global soup_input
    soup_Routine.ApplySelections(soup_input, soup_Window.id_Items, soup_Window.collect_coins, soup_Window.collect_events, soup_Window.collect_items_white, soup_Window.collect_items_blue, \
                soup_Window.collect_items_grape, soup_Window.collect_items_gold, soup_Window.collect_dye, soup_Window.sell_items, soup_Window.sell_items_white, \
                soup_Window.sell_items_blue, soup_Window.sell_items_grape, soup_Window.sell_items_gold, soup_Window.sell_items_green, soup_Window.sell_materials, soup_Window.salvage_items, soup_Window.salvage_items_white, \
                soup_Window.salvage_items_blue, soup_Window.salvage_items_grape, soup_Window.salvage_items_gold)

def ApplySoupConfigSettings(min_slots):
    soup_Routine.ApplyConfigSettings(min_slots)

def StartBot():
    ApplyLootAndMerchantSelections()
    soup_Routine.Start()

def StopBot():
    if soup_Routine.IsBotRunning():
        soup_Routine.Stop()

def ResetBot():
    # Stop the main state machine  
    soup_Routine.Stop()
    soup_Routine.Reset()

def PrintData():
    soup_Routine.PrintData()

def GetRunTime():
    return soup_Routine.GetCurrentRunTime()

def GetAverageRunTime():
    return soup_Routine.GetAverageTime()

def GetTotalRunTime():
    return soup_Routine.GetTotalTime()

# def StartBot():
#     global soup_input
#     soup_Routine.ApplySelections(soup_input, soup_Window.id_Items, soup_Window.collect_coins, soup_Window.collect_events, soup_Window.collect_items_white, soup_Window.collect_items_blue, \
#                 soup_Window.collect_items_grape, soup_Window.collect_items_gold, soup_Window.collect_dye, soup_Window.sell_items, soup_Window.sell_items_white, \
#                 soup_Window.sell_items_blue, soup_Window.sell_items_grape, soup_Window.sell_items_gold, soup_Window.sell_items_green, soup_Window.sell_materials, soup_Window.salvage_items, soup_Window.salvage_items_white, \
#                 soup_Window.salvage_items_blue, soup_Window.salvage_items_grape, soup_Window.salvage_items_gold)
#     soup_Routine.Start()

# def StopBot():
#     if soup_Routine.IsBotRunning():
#         soup_Routine.Stop()

# def ResetBot():
#     # Stop the main state machine  
#     soup_Routine.Stop()
#     soup_Routine.Reset()

# def PrintData():
#     soup_Routine.PrintData()

### --- MAIN --- ###
def main():
    try:
        if soup_Window:
            soup_Window.Show()

        # Could just put a main timer here and only fire the updates in some interval, but I like more control specific to tasks (eg. Staying Alive, Kill, Loot, etc)
        if Party.IsPartyLoaded():
            if soup_Routine and soup_Routine.IsBotRunning():
                soup_Routine.Update()
                
    except ImportError as e:
        Py4GW.Console.Log(bot_name, f"ImportError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except ValueError as e:
        Py4GW.Console.Log(bot_name, f"ValueError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except TypeError as e:
        Py4GW.Console.Log(bot_name, f"TypeError encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    except Exception as e:
        Py4GW.Console.Log(bot_name, f"Unexpected error encountered: {str(e)}", Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_name, f"Stack trace: {traceback.format_exc()}", Py4GW.Console.MessageType.Error)
    finally:
        pass

if __name__ == "__main__":
    main()

### -- MAIN -- ###