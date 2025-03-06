from Py4GWCoreLib import *
from BotUtilities import *
from WindowUtilites import *

import Items
import Mapping

bot_name = "Nikons Kabob Farm"

kabob_selected = True
do_kabob_exchange = False
kabob_input = 250
show_about_popup = False

class Kabob_Window(BasicWindow):
    global kabob_selected
    
    kabob_original_size = [350.0, 400.0]
    kabob_explanded_size = [350.0, 475.0]

    def __init__(self, window_name="Basic Window", window_size = [350.0, 470.0], show_logger = True, show_state = True):
        super().__init__(window_name, window_size, show_logger, show_state)

    def ShowMainControls(self):
        global kabob_selected, kabob_input, do_kabob_exchange, show_about_popup

        if PyImGui.collapsing_header("About"):            
            PyImGui.text("- Required Quest: Drakes on the Plain")
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
            PyImGui.text(f"- Will not sell Drake Flesh, Salv or Id kits.")

        PyImGui.separator()
        PyImGui.begin_child("MainCollectPanel", (0.0, 70.0), False, 0)
        if PyImGui.begin_table("Collect_Inputs", 2):
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            kabob_selected = PyImGui.checkbox("Farm Drake Flesh", kabob_selected)  
            PyImGui.table_next_column()
            kabob_input = PyImGui.input_int("# Flesh", kabob_input) if kabob_input >= 0 else 0 
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            do_kabob_exchange = PyImGui.checkbox("Exchange Drake Flesh", do_kabob_exchange)  
            PyImGui.end_table()
        PyImGui.end_child()
        PyImGui.separator()

    def ShowResults(self):
        global kabob_input

        PyImGui.separator()
        PyImGui.text("Results:")

        if PyImGui.begin_table("Runs_Results", 5):
            kabob_data = GetKabobData()
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            PyImGui.text(f"Runs: {kabob_data[0]}")
            PyImGui.table_next_column()
            PyImGui.text(f"Success: ")
            PyImGui.table_next_column()
            PyImGui.text_colored(f"{kabob_data[1]}", (0, 1, 0, 1))
            PyImGui.table_next_column()
            PyImGui.text(f"Fails:")
            PyImGui.table_next_column()
            fails = kabob_data[0] - kabob_data[1]

            if fails > 0:
                PyImGui.text_colored(f"{fails}", (1, 0, 0, 1))
            else:
                PyImGui.text(f"{fails}")

            PyImGui.table_next_row()
            PyImGui.end_table()

        if PyImGui.begin_table("Collect_Results", 3):  # Use begin_table for starting a table
            # Drake Kabob
            PyImGui.table_next_row()
            PyImGui.table_next_column()
            PyImGui.text("Kabobs:")
            PyImGui.table_next_column()
            if kabob_selected and kabob_input > 0 and GetKabobCollected() == 0:            
                PyImGui.text_colored(f"{GetKabobCollected()}", (1, 0, 0, 1))
            else:
                PyImGui.text_colored(f"{GetKabobCollected()}", (0, 1, 0, 1))
            PyImGui.table_next_column()
            PyImGui.text(f"collected of {kabob_input}")

            PyImGui.table_next_row()
            PyImGui.end_table()

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

            PyImGui.table_next_row()
            PyImGui.end_table()

    def ApplyLootMerchantSettings(self):
        return ApplyLootAndMerchantSelections()

    def GetKabobSettings(self):
        global kabob_input

        return (kabob_input, self.id_Items, self.collect_coins, self.collect_events, self.collect_items_white, self.collect_items_blue, \
                self.collect_items_grape, self.collect_items_gold, self.collect_dye, self.sell_items, self.sell_items_white, \
                self.sell_items_blue, self.sell_items_grape, self.sell_items_gold, self.sell_materials, self.salvage_items, self.salvage_items_white, \
                self.salvage_items_blue, self.salvage_items_grape, self.salvage_items_gold)
                
class Kabob_Farm(ReportsProgress):
    class Kabob_Skillbar:    
        def __init__(self):
            self.sand_shards = SkillBar.GetSkillIDBySlot(1)
            self.vos = SkillBar.GetSkillIDBySlot(2)
            self.staggering = SkillBar.GetSkillIDBySlot(3)
            self.eremites = SkillBar.GetSkillIDBySlot(4)
            self.intimidating = SkillBar.GetSkillIDBySlot(5)
            self.sanctity = SkillBar.GetSkillIDBySlot(6)
            self.regen = SkillBar.GetSkillIDBySlot(7)
            self.hos = SkillBar.GetSkillIDBySlot(8)

    # Kabob_Routine is the FSM instance
    Kabob_Routine = FSM("Kabob_Main")
    Kabob_Exchange_Routine = FSM("Kabob_Exchange")
    inventoryRoutine = InventoryFsm(None, None, 0, None, None)

    Kabob_Skillbar_Code = "Ogek8Np5Kzmj59brdbu731L7FBC"
    Kabob_Hero_Skillbar_Code = "OQkiUxm8sjJxsYAAAAAAAAAA"

    kabob_exchange_travel = "Kabob- Exchange Travel Kamadan"
    kabob_exchange_wait_map = "Kabob- Exchange Waiting Map"
    kabob_exchange_move_to_collector = "Kabob- Exchange Go to Chef"
    kabob_exchange_target_collector = "Kabob- Exchange Target"
    kabob_exchange_interact_collector = "Kabob- Exchange Interact"
    kabob_exchange_do_exchange_all = "Kabob- Exchange Kabobs"
    kabob_exchange_Kabobs_routine_start = "Kabob- Go Exchange Kabobs#1"
    kabob_exchange_Kabobs_routine_end = "Kabob- Go Exchange Kabobs#2"
    
    kabob_inventory_routine = "DoInventoryRoutine"
    kabob_initial_check_inventory = "Kabob- Inventory Check"
    kabob_check_inventory_after_handle_inventory = "Kabob- Inventory Handled?"
    kabob_travel_state_name = "Kabob- Traveling to Rihlon"
    kabob_set_normal_mode = "Kabob- Set Normal Mode"
    kabob_add_hero_state_name = "Kabob- Adding Koss"
    kabob_load_skillbar_state_name = "Kabob- Load Skillbar"
    kabob_pathing_1_state_name = "Kabob- Leaving Outpost 1"
    kabob_resign_pathing_state_name = "Kabob- Setup Resign"
    kabob_pathing_2_state_name = "Kabob- Leaving Outpost 2"
    kabob_waiting_map_state_name = "Kabob- Farm Map Loading"
    kabob_change_weapon_staff = "Kabob- Change to Staff"
    kabob_change_weapon_scythe = "Kabob- Change to Scythe"
    kabob_kill_koss_state_name = "Kabob- Killing Koss"
    kabob_waiting_run_state_name = "Kabob- Move to Farm Spot"
    kabob_waiting_kill_state_name = "Kabob- Killing Drakes"
    kabob_looting_state_name = "Kabob- Picking Up Loot"
    kabob_resign_state_name = "Kabob- Resigning"
    kabob_wait_return_state_name = "Kabob- Wait Return"
    kabob_inventory_state_name = "Kabob- Handle Inventory"
    kabob_inventory_state_name_end = "Kabob-Handle Inventory#2"
    kabob_end_state_name = "Kabob- End Routine"
    kabob_forced_stop = "Kabob- End Forced"
    kabob_outpost_portal = [(-15022, 8470)] # Used by itself if spawn close to Floodplain portal
    kabob_outpost_pathing = [(-15480, 11138), (-16009, 10219), (-15022, 8470)] # Used when spawn location is near xunlai chest or merchant
    kabob_farm_run_pathing = [(-14512, 8238), (-12469, 9387), (-12243, 10163), (-10703, 10952), (-10066, 11265), (-9595, 11343), (-8922, 11625), (-8501, 11756)]
    kabob_outpost_resign_pathing = [(-15743, 9784)]
    kabob_merchant_position = [(-15082, 11368)]
    kabob_pathing_portal_only_handler_1 = Routines.Movement.PathHandler(kabob_outpost_portal)
    kabob_pathing_portal_only_handler_2 = Routines.Movement.PathHandler(kabob_outpost_portal)
    kabob_pathing_resign_portal_handler = Routines.Movement.PathHandler(kabob_outpost_resign_pathing)
    kabob_pathing_move_to_portal_handler = Routines.Movement.PathHandler(kabob_outpost_pathing)
    kabob_pathing_move_to_kill_handler = Routines.Movement.PathHandler(kabob_farm_run_pathing)
    
    kabob_exchange_pathing = [(-8400, 14155), (-11170, 15188)]
    kabob_exchange_pathing_handler = Routines.Movement.PathHandler(kabob_exchange_pathing)
    movement_Handler = Routines.Movement.FollowXY(50)
    
    keep_list = []
    keep_list.extend(Items.IdSalveItems_Array)  #[(Items.Drake_Flesh), (Items.Salve_Kit_Basic), (Items.Salve_Kit_Advanced), (Items.Salve_Kit_Superior), (Items.Id_Kit_Basic), (Items.Id_Kit_Superior)]
    keep_list.extend(Items.EventItems_Array)
    keep_list.append(Items.Drake_Flesh)
    keep_list.append(Items.Dye.Dye_ModelId)
    
    kabob_first_after_reset = False
    kabob_wait_to_kill = False
    kabob_ready_to_kill = False
    kabob_killing_staggering_casted = False
    kabob_killing_eremites_casted = False
    #kabob_sanctity = False
    #kabob_intimidating = False

    player_stuck = False
    player_stuck_hos_count = 0
    player_skill_load_count = 0

    weapon_slot_staff = 1
    weapon_slot_scythe = 2
    kabob_collected = 0
    add_koss_tries = 0
    current_lootable = 0
    current_loot_tries = 0
    
    kabob_runs = 0
    kabob_success = 0
    kabob_fails = 0
    
    second_timer_elapsed = 1000
    loot_timer_elapsed = 1500

    skillBar = Kabob_Skillbar()
    
    pyParty = PyParty.PyParty()
    pyMerchant = PyMerchant.PyMerchant()
    kabob_exchange_timer = Timer()
    kabob_second_timer = Timer()
    kabob_step_done_timer = Timer()
    kabob_stuck_timer = Timer()
    kabob_loot_timer = Timer()
    kabob_loot_done_timer = Timer()
    kabob_stay_alive_timer = Timer()

    current_inventory = []
    stuckPosition = []

    ### --- SETUP --- ###
    def __init__(self, window):
        super().__init__(window)
        self.skillBar = self.Kabob_Skillbar()

        self.current_inventory = GetInventoryItemSlots()
        self.inventoryRoutine = InventoryFsm(window, self.kabob_inventory_routine, Mapping.Rilohn_Refuge, 
                                             self.kabob_merchant_position, self.current_inventory, 
                                             self.keep_list, goldToKeep=5000, logFunc=self.Log)
        
        self.Kabob_Exchange_Routine.AddState(self.kabob_exchange_travel,
                                             execute_fn=lambda: self.ExecuteStep(self.kabob_exchange_travel, Routines.Transition.TravelToOutpost(Mapping.Kamadan)),
                                             exit_condition=lambda: Routines.Transition.HasArrivedToOutpost(Mapping.Kamadan),
                                             transition_delay_ms=1000)
        self.Kabob_Exchange_Routine.AddState(self.kabob_exchange_move_to_collector,
                                             execute_fn=lambda: self.ExecuteStep(self.kabob_exchange_move_to_collector, Routines.Movement.FollowPath(self.kabob_exchange_pathing_handler, self.movement_Handler)),
                                             exit_condition=lambda: Routines.Movement.IsFollowPathFinished(self.kabob_exchange_pathing_handler, self.movement_Handler),
                                             run_once=False)
        
        self.Kabob_Exchange_Routine.AddState(name=self.kabob_exchange_target_collector,
                                             execute_fn=lambda: self.ExecuteStep(self.kabob_exchange_target_collector, TargetNearestNpc()),
                                             transition_delay_ms=1000)
        
        self.Kabob_Exchange_Routine.AddState(name=self.kabob_exchange_interact_collector,
                                             execute_fn=lambda: self.ExecuteStep(self.kabob_exchange_interact_collector, Routines.Targeting.InteractTarget()),
                                             exit_condition=lambda: Routines.Targeting.HasArrivedToTarget())
        
        self.Kabob_Exchange_Routine.AddState(name=self.kabob_exchange_do_exchange_all,
                                             execute_fn=lambda: self.ExecuteStep(self.kabob_exchange_do_exchange_all, self.ExchangeKabobs()),
                                             exit_condition=lambda: self.ExchangeKabobsDone(), 
                                             run_once=False)
        
        self.Kabob_Routine.AddSubroutine(self.kabob_exchange_Kabobs_routine_start,
                                         sub_fsm=self.Kabob_Exchange_Routine,
                                         condition_fn=lambda: self.CheckExchangeKabobs() and CheckIfInventoryHasItem(Items.Drake_Flesh))        
        self.Kabob_Routine.AddState(self.kabob_travel_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_travel_state_name, Routines.Transition.TravelToOutpost(Mapping.Rilohn_Refuge)),
                       exit_condition=lambda: Routines.Transition.HasArrivedToOutpost(Mapping.Rilohn_Refuge),
                       transition_delay_ms=1000)
        self.Kabob_Routine.AddState(self.kabob_initial_check_inventory, execute_fn=lambda: self.CheckInventory())
        self.Kabob_Routine.AddState(self.kabob_set_normal_mode,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_set_normal_mode, Party.SetNormalMode()),
                       transition_delay_ms=1000)
        self.Kabob_Routine.AddState(self.kabob_add_hero_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_add_hero_state_name, self.PutKossInParty()), # Ensure only one hero in party
                       transition_delay_ms=1000)
        self.Kabob_Routine.AddState(self.kabob_load_skillbar_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_load_skillbar_state_name, self.LoadSkillBar()), # Ensure only one hero in party                       
                       exit_condition=lambda: self.IsSkillBarLoaded(),
                       transition_delay_ms=1500)
        self.Kabob_Routine.AddState(self.kabob_pathing_1_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_pathing_1_state_name, Routines.Movement.FollowPath(self.kabob_pathing_portal_only_handler_1, self.movement_Handler)),
                       exit_condition=lambda: Routines.Movement.IsFollowPathFinished(self.kabob_pathing_portal_only_handler_1, self.movement_Handler) or Map.GetMapID() == Mapping.Floodplain_Of_Mahnkelon,
                       run_once=False)
        self.Kabob_Routine.AddState(self.kabob_resign_pathing_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_resign_pathing_state_name, Routines.Movement.FollowPath(self.kabob_pathing_resign_portal_handler, self.movement_Handler)),
                       exit_condition=lambda: Map.GetMapID() == Mapping.Rilohn_Refuge and Party.IsPartyLoaded(), # or Routines.Movement.IsFollowPathFinished(kabob_pathing_resign_portal_handler, movement_Handler) or Map.GetMapID() == Mapping.Rilohn_Refuge,
                       run_once=False)
        self.Kabob_Routine.AddSubroutine(self.kabob_inventory_state_name,
                       sub_fsm = self.inventoryRoutine, # dont add execute function wrapper here
                       condition_fn=lambda: not self.kabob_first_after_reset and Inventory.GetFreeSlotCount() <= self.default_min_slots)        
        self.Kabob_Routine.AddState(self.kabob_check_inventory_after_handle_inventory, execute_fn=lambda: self.CheckInventory())
        self.Kabob_Routine.AddState(self.kabob_change_weapon_staff,
                                    execute_fn=lambda: self.ExecuteStep(self.kabob_change_weapon_staff, ChangeWeaponSet(self.weapon_slot_staff)),
                                    #exit_condition=lambda: CheckWeaponEquipped("Staff", self.Log),
                                    transition_delay_ms=1000)
        self.Kabob_Routine.AddState(self.kabob_pathing_2_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_pathing_2_state_name, Routines.Movement.FollowPath(self.kabob_pathing_portal_only_handler_2, self.movement_Handler)),
                       exit_condition=lambda: Routines.Movement.IsFollowPathFinished(self.kabob_pathing_portal_only_handler_2, self.movement_Handler) or Map.GetMapID() == Mapping.Floodplain_Of_Mahnkelon,
                       run_once=False)
        self.Kabob_Routine.AddState(self.kabob_waiting_map_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_waiting_map_state_name, Routines.Transition.IsExplorableLoaded()),
                       transition_delay_ms=1000)
        self.Kabob_Routine.AddState(self.kabob_kill_koss_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_kill_koss_state_name, self.KillKoss()),
                       transition_delay_ms=1000)
        self.Kabob_Routine.AddState(self.kabob_waiting_run_state_name,
                       execute_fn=lambda: self.ExecuteTimedStep(self.kabob_waiting_run_state_name, self.TimeToRunToDrakes()),
                       exit_condition=lambda: self.RunToDrakesDone(),
                       run_once=False)
        self.Kabob_Routine.AddState(self.kabob_change_weapon_scythe,
                            execute_fn=lambda: self.ExecuteStep(self.kabob_change_weapon_scythe, ChangeWeaponSet(self.weapon_slot_scythe)),
                            #exit_condition=lambda: CheckWeaponEquipped("Scythe", self.Log),
                            transition_delay_ms=1000)
        self.Kabob_Routine.AddState(self.kabob_waiting_kill_state_name,
                       execute_fn=lambda: self.ExecuteTimedStep(self.kabob_waiting_kill_state_name, self.KillLoopStart()),
                       exit_condition=lambda: self.KillLoopComplete() or self.ShouldForceTransitionStep(),
                       run_once=False)
        self.Kabob_Routine.AddState(self.kabob_looting_state_name,
                       execute_fn=lambda: self.ExecuteTimedStep(self.kabob_looting_state_name, self.LootLoopStart()),
                       exit_condition=lambda: self.LootLoopComplete() or self.ShouldForceTransitionStep(),
                       run_once=False)
        self.Kabob_Routine.AddState(self.kabob_resign_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_resign_state_name, Player.SendChatCommand("resign")),
                       exit_condition=lambda: Agent.IsDead(Player.GetAgentID()) or Map.GetMapID() == Mapping.Rilohn_Refuge,
                       transition_delay_ms=3000)
        self.Kabob_Routine.AddState(self.kabob_wait_return_state_name,
                       execute_fn=lambda: self.ExecuteTimedStep(self.kabob_wait_return_state_name, Party.ReturnToOutpost()),
                       exit_condition=lambda: Map.GetMapID() == Mapping.Rilohn_Refuge and Party.IsPartyLoaded() or self.ShouldForceTransitionStep(),
                       transition_delay_ms=3000)
        self.Kabob_Routine.AddState(self.kabob_end_state_name,
                       execute_fn=lambda: self.ExecuteStep(self.kabob_end_state_name, self.CheckKabobRoutineEnd()),
                       transition_delay_ms=1000)        
        self.Kabob_Routine.AddSubroutine(self.kabob_inventory_state_name_end,
                       sub_fsm = self.inventoryRoutine)       
        self.Kabob_Routine.AddSubroutine(self.kabob_exchange_Kabobs_routine_end,
                                         condition_fn=lambda: self.CheckExchangeKabobs() and CheckIfInventoryHasItem(Items.Drake_Flesh))
        self.Kabob_Routine.AddState(self.kabob_forced_stop,                                    
                                    execute_fn=lambda: self.ExecuteStep(self.kabob_change_weapon_scythe, None))

    def CheckExchangeKabobs(self):
        global do_kabob_exchange
        self.Log(f"Check Kabob Exchange: {do_kabob_exchange}")
        return do_kabob_exchange
    
    # Start the kabob routine from the first state after soft reset in case player moved around.
    def Start(self):
        if self.Kabob_Routine and not self.Kabob_Routine.is_started():
            self.SoftReset()
            self.Kabob_Routine.start()
            self.window.StartBot()

    # Stop the kabob routine.
    def Stop(self):
        if not self.Kabob_Routine:
            return
        
        if self.Kabob_Routine.is_started():
            self.Kabob_Routine.stop()
            self.window.StopBot()

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
        if self.Kabob_Routine:
            self.Kabob_Routine.reset()
            self.Kabob_Routine.stop()
        
        self.kabob_collected = 0    
        self.kabob_runs = 0
        self.kabob_success = 0
        self.kabob_fails = 0

        self.kabob_first_after_reset = True      

        self.SoftReset()

        # Get new set of inventory slots to keep around in case player went and did some shit, then came back
        self.window.ResetBot()

    def SoftReset(self):
        self.player_stuck = False
        self.kabob_wait_to_kill = False
        self.kabob_ready_to_kill = False
        self.kabob_killing_staggering_casted = False
        self.kabob_killing_eremites_casted = False
        self.step_transition_threshold_timer.Reset()
        
        self.add_koss_tries = 0
        self.player_stuck_hos_count = 0
        self.current_lootable = 0
        self.current_loot_tries = 0

        #kabob_Window.kabob_id_items, kabob_Window.kabob_collect_coins, kabob_Window.kabob_collect_events, kabob_Window.kabob_collect_items_white, kabob_Window.kabob_collect_items_blue, \
        #kabob_Window.kabob_collect_items_grape, kabob_Window.kabob_collect_items_gold, kabob_Window.kabob_collect_dye
        
        self.inventoryRoutine.Reset()
        self.inventoryRoutine.ApplySelections(idItems=self.idItems, sellItems=self.sellItems, sellWhites=self.sellWhites, 
                                             sellBlues=self.sellBlues, sellGrapes=self.sellGrapes, sellGolds=self.sellGolds, sellGreens=self.sellGreens, 
                                             sellMaterials=self.sellMaterials, salvageItems=self.salvageItems, salvWhites=self.salvWhites, salvBlue=self.salvBlues,
                                             salvGrapes=self.salvGrapes, salvGolds=self.salvGold)
        self.ResetPathing()

    def ResetPathing(self):        
        self.movement_Handler.reset()
        self.kabob_loot_timer.Stop()
        self.kabob_loot_done_timer.Stop()
        self.kabob_stuck_timer.Stop()
        self.kabob_second_timer.Stop()
        self.kabob_stay_alive_timer.Stop()
        self.kabob_step_done_timer.Stop()
        self.kabob_pathing_move_to_kill_handler.reset()
        self.kabob_pathing_resign_portal_handler.reset()
        self.kabob_pathing_portal_only_handler_1.reset()
        self.kabob_pathing_portal_only_handler_2.reset()
        self.kabob_pathing_move_to_portal_handler.reset()

    def IsBotRunning(self):
        return self.Kabob_Routine.is_started() and not self.Kabob_Routine.is_finished()

    def Update(self):
        if self.Kabob_Routine.is_started() and not self.Kabob_Routine.is_finished():
            self.Kabob_Routine.update()

    def Resign(self):
        if self.Kabob_Routine.is_started():
            self.kabob_runs += 1
            self.Kabob_Routine.jump_to_state_by_name(self.kabob_resign_state_name)

    def SuccessResign(self):
        self.Resign()
        self.kabob_success += 1

    def FailResign(self):
        self.Resign()
        self.kabob_fails += 1

    def ExchangeKabobs(self):
        if not self.kabob_exchange_timer.IsRunning():
            self.kabob_exchange_timer.Start()

        if not self.kabob_exchange_timer.HasElapsed(40):
            return
        
        self.kabob_exchange_timer.Reset()

        try:
            turn_in = GetItemIdFromModelId(Items.Drake_Flesh)

            self.Log(f"Kabob Item Id: {turn_in}")
            if turn_in == 0:
                return
            
            items3 = self.pyMerchant.get_merchant_item_list()
                
            if items3:
                for item in items3:
                    if Item.GetModelID(item) == Items.Drake_Kabob:
                        self.Log(f"Trading: {item} for a kabob")
                        self.pyMerchant.collector_buy_item(item, 0, [turn_in], [1])

        except Exception as e:
            self.Log(f"Error in Exchanging Kabobs: {str(e)}", Py4GW.Console.MessageType.Error)

    def ExchangeKabobsDone(self):
        return not CheckIfInventoryHasItem(Items.Drake_Flesh)

    def CheckSurrounded(self):
        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), GameAreas.Lesser_Earshot)
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')

        return len(enemy_array) > 7 or self.player_stuck
    
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
            self.Kabob_Routine.jump_to_state_by_name(self.kabob_forced_stop)      
        elif secondary != "Assassin":
            self.Log("Bot Requires Assassin Secondary")
            self.Kabob_Routine.jump_to_state_by_name(self.kabob_forced_stop)      
        else:
            SkillBar.LoadSkillTemplate(self.Kabob_Skillbar_Code)

            # Dont really care about koss if he doesnt have the skills, but try to set a build anyway
            SkillBar.LoadHeroSkillTemplate (1, self.Kabob_Hero_Skillbar_Code)
    
    def IsSkillBarLoaded(self):
        primary_profession, secondary = Agent.GetProfessionNames(Player.GetAgentID())
        
        if primary_profession != "Dervish":        
            self.Log("Bot Requires Dervish Primary", Py4GW.Console.MessageType.Error)
            self.Kabob_Routine.jump_to_state_by_name(self.kabob_forced_stop)   
            return False        
        elif secondary != "Assassin":
            self.Log("Bot Requires Assassin Secondary")
            self.Kabob_Routine.jump_to_state_by_name(self.kabob_forced_stop)
            return False
        else:
            if SkillBar.GetSkillIDBySlot(1) == 0 or SkillBar.GetSkillIDBySlot(2) == 0 or \
            SkillBar.GetSkillIDBySlot(3) == 0 or SkillBar.GetSkillIDBySlot(4) == 0 or \
            SkillBar.GetSkillIDBySlot(5) == 0 or SkillBar.GetSkillIDBySlot(6) == 0 or \
            SkillBar.GetSkillIDBySlot(7) == 0 or SkillBar.GetSkillIDBySlot(8) == 0:
                player_skill_load_count += 1
                if player_skill_load_count > 10:
                    self.Log("Unable to Load Skills")
                    self.Kabob_Routine.jump_to_state_by_name(self.kabob_forced_stop)
                return False
            return True

    def PutKossInParty(self):
        self.pyParty.LeaveParty()
        self.pyParty.AddHero(Heroes.Koss)

    def IsKossInParty(self):
        if not IsHeroInParty(Heroes.Koss):
            self.add_koss_tries += 1

        # If Koss not added after ~5 seconds, fail and end kabob farming.
        if self.add_koss_tries >= 5:
            self.Log("Unable to add Koss to Party!")
            self.Stop()
            return True
        
        return False
    
    def KillKoss(self):
        agent_id = Player.GetAgentID()
        SkillBar.HeroUseSkill(agent_id, 2, 1)
        SkillBar.HeroUseSkill(agent_id, 3, 1)
        SkillBar.HeroUseSkill(agent_id, 1, 1)
        
        self.pyParty.FlagHero(self.pyParty.GetHeroAgentID(1), -16749, 5382)

    def TimeToRunToDrakes(self):
        if not self.kabob_second_timer.IsRunning():
            self.kabob_second_timer.Start()

        if not self.kabob_second_timer.HasElapsed(100):
            return
        
        self.kabob_second_timer.Reset()
                      
        try:
            if Agent.IsDead(Player.GetAgentID()):
                self.FailResign()
                return
                
            # Checking whether the player is stuck
            self.HandleStuck()

            # Run the stay alive script.
            self.StayAliveLoop()

            # Try to follow the path based on pathing points and movement handler.
            Routines.Movement.FollowPath(self.kabob_pathing_move_to_kill_handler, self.movement_Handler)
        except Exception as e:
            Py4GW.Console.Log("Run To Drakes", str(e), Py4GW.Console.MessageType.Error)

    def RunToDrakesDone(self):
        if not self.kabob_step_done_timer.IsRunning():
            self.kabob_step_done_timer.Start()

        if not self.kabob_step_done_timer.HasElapsed(500):
            return False
        
        self.kabob_step_done_timer.Reset()

        pathDone = Routines.Movement.IsFollowPathFinished(self.kabob_pathing_move_to_kill_handler, self.movement_Handler)         
        surrounded = self.CheckSurrounded()
        forceStep = self.ShouldForceTransitionStep()

        return pathDone or surrounded or forceStep

    def KillLoopStart(self):
        self.StayAliveLoop()
        self.Kill()

    # Stay alive using all heal buffs and hos if available
    def StayAliveLoop(self):
        if not self.kabob_stay_alive_timer.IsRunning():
            self.kabob_stay_alive_timer.Start()

        if not self.kabob_stay_alive_timer.HasElapsed(1000):
            return
        
        self.kabob_stay_alive_timer.Reset()

        try:            
            player_id = Player.GetAgentID()

            if Agent.IsDead(player_id):
                self.FailResign()
                return
                
            if not CanCast(player_id):
                return
             
            if self.kabob_killing_staggering_casted:
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
                        if not IsEnemyInFront(enemies[0]):
                            for enemy in enemies:
                                if IsEnemyInFront(enemy):
                                    break

                    if HasEnoughEnergy(self.skillBar.hos) and IsSkillReadyById(self.skillBar.hos):
                        CastSkillById(self.skillBar.hos)

                        if self.player_stuck:
                            self.player_stuck_hos_count += 1

                            if self.player_stuck_hos_count > 2:
                                # kill shit then if not already
                                self.kabob_ready_to_kill = True
                                self.Kabob_Routine.jump_to_state_by_name(self.kabob_waiting_kill_state_name)
                                return
                        return
                    
                regen_time_remain = 0
                intimidate_time_remain = 0
                sanctity_time_remain = 0 
                                  
                player_buffs = Effects.GetEffects(player_id)

                for buff in player_buffs:
                    if buff.skill_id == self.skillBar.regen:
                        regen_time_remain = buff.time_remaining
                    if buff.skill_id == self.skillBar.intimidating:
                        intimidate_time_remain = buff.time_remaining
                    if buff.skill_id == self.skillBar.sanctity:
                        sanctity_time_remain = buff.time_remaining                    

                if regen_time_remain < 3000 and HasEnoughEnergy(self.skillBar.regen) and IsSkillReadyById(self.skillBar.regen):
                    CastSkillById(self.skillBar.regen)
                    return
                
                hasShards = HasBuff(player_id, self.skillBar.sand_shards)

                if not hasShards and IsSkillReadyById(self.skillBar.sand_shards) and HasEnoughEnergy(self.skillBar.sand_shards) and len(enemies) > 1:
                    CastSkillById(self.skillBar.sand_shards)
                    return
                                 
                # Only cast these when waiting for the killing to start.
                if self.Kabob_Routine.get_current_step_name() == self.kabob_waiting_kill_state_name or hp < dangerHp:
                    if intimidate_time_remain < 3000 and HasEnoughEnergy(self.skillBar.intimidating) and IsSkillReadyById(self.skillBar.intimidating):
                        CastSkillById(self.skillBar.intimidating)
                        return

                    if sanctity_time_remain < 3000 and HasEnoughEnergy(self.skillBar.sanctity) and IsSkillReadyById(self.skillBar.sanctity):
                        CastSkillById(self.skillBar.sanctity)
        except Exception as e:
            Py4GW.Console.Log("StayAlive", str(e), Py4GW.Console.MessageType.Error)

    def Kill(self):
        if not self.kabob_second_timer.IsRunning():
            self.kabob_second_timer.Start()

        if not self.kabob_second_timer.HasElapsed(1000):
            return
        
        self.kabob_second_timer.Reset()

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

                    if len(enemies) == 0:
                        enemies = AgentArray.GetEnemyArray()
                        enemies = AgentArray.Filter.ByDistance(enemies, Player.GetXY(), GameAreas.Earshot)
                        enemies = AgentArray.Filter.ByAttribute(enemies, 'IsAlive')

                        if len(enemies) > 0:
                            if HasEnoughEnergy(self.skillBar.hos) and IsSkillReadyById(self.skillBar.hos):
                                CastSkillById(self.skillBar.hos)
                        return
                                                            
                    if not self.kabob_ready_to_kill:
                        if len(enemies) < 7 and not self.player_stuck:
                            return
                        
                        self.kabob_ready_to_kill = True

                        # Use hos so we get them balled up a bit better (sometimes)
                        if not IsEnemyInFront(enemies[0]):
                            for enemy in enemies:
                                if IsEnemyInFront(enemy):
                                    break

                        if HasEnoughEnergy(self.skillBar.hos) and IsSkillReadyById(self.skillBar.hos):
                            CastSkillById(self.skillBar.hos)
                            return
                    
                    # Ensure have damage mitigation up before attacking
                    if len(enemies) > 1 and (not HasBuff(player_id, self.skillBar.intimidating) or not HasBuff(player_id, self.skillBar.sanctity)):
                        return
                    
                    target = Player.GetTargetID()

                    if target not in enemies:
                        target = enemies[0]

                    Player.ChangeTarget(target)
                        
                    if self.kabob_killing_staggering_casted and IsSkillReadyById(self.skillBar.eremites) and HasEnoughEnergy(self.skillBar.eremites):  
                        self.kabob_killing_staggering_casted = False
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

                    if not self.kabob_killing_staggering_casted and not hasShards and IsSkillReadyById(self.skillBar.sand_shards) and HasEnoughEnergy(self.skillBar.sand_shards) and len(enemies) > 1:
                        # self.Log("shards")
                        CastSkillById(self.skillBar.sand_shards)
                        return
                                            
                    # Get Ready for killing
                    # Need find a way to change weapon set since  sending the change keys is not working for F1-F4
                    # For now assume we're good to go.
                    if not self.kabob_killing_staggering_casted and vos_time_remain < 3000 and IsSkillReadyById(self.skillBar.vos) and HasEnoughEnergy(self.skillBar.vos):                        
                        # self.Log("vos")
                        CastSkillById(self.skillBar.vos)
                        return
                        
                    if IsSkillReadyById(self.skillBar.eremites) and HasEnoughEnergy(self.skillBar.eremites):
                        if IsSkillReadyById(self.skillBar.staggering) and HasEnoughEnergy(self.skillBar.staggering):
                            self.kabob_killing_staggering_casted = True
                            # self.Log("stagger")
                            CastSkillById(self.skillBar.staggering)
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
        # Check if our item is a kabob first, otherwise let base hangle it.
        item = Agent.GetItemAgent(agentId)

        if item:     
            model = Item.GetModelID(item.item_id)

            if model == Items.Drake_Flesh:
                return True
            else:
                return super().CanPickUp(agentId)
              
        return False
    
    def LootLoopStart(self):
        try:
            if not self.kabob_loot_timer.IsRunning():
                self.kabob_loot_timer.Start()

            if self.kabob_loot_timer.HasElapsed(self.loot_timer_elapsed):                
                self.kabob_loot_timer.Reset()

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
                    self.kabob_collected += 1

                Player.Interact(item)
        except Exception as e:
            Py4GW.Console.Log("Loot Loop", f"Error during looting {str(e)}", Py4GW.Console.MessageType.Error)

    def LootLoopComplete(self):
        try:
            if not self.kabob_loot_done_timer.IsRunning():
                self.kabob_loot_done_timer.Start()

            if self.kabob_loot_done_timer.HasElapsed(self.loot_timer_elapsed):
                self.kabob_loot_done_timer.Reset()

                if self.current_lootable == 0 or Inventory.GetFreeSlotCount() == 0:                    
                    self.kabob_runs += 1
                    self.kabob_success += 1
                    return True

                # item = self.GetNearestPickupItem()
                # if item == 0 or item == None or Inventory.GetFreeSlotCount() == 0:
                #     self.kabob_runs += 1
                #     self.kabob_success += 1
                #     return True

            return False
        except Exception as e:
            Py4GW.Console.Log("Loot Loop Complete", f"Error during looting {str(e)}", Py4GW.Console.MessageType.Error)
    
    def GetKabobCollected(self):
        return self.kabob_collected

    def GetKabobStats(self):
        return (self.kabob_runs, self.kabob_success)
    
    # Jump back to output pathing if not done collecting
    def CheckKabobRoutineEnd(self):
        # Don't reset the kabob count
        self.SoftReset()

        self.kabob_first_after_reset = False

        if self.kabob_collected < self.main_item_collect:
            # mapping to outpost may have failed OR the threshold was reached. Try to map there and start over.
            if Map.GetMapID() != Mapping.Rilohn_Refuge:
                self.Kabob_Routine.jump_to_state_by_name(self.kabob_travel_state_name)
            else:
                # already at outpost, check slot count, handle inv or continue farm
                if Inventory.GetFreeSlotCount() <= self.default_min_slots:
                    self.UpdateState(self.kabob_inventory_state_name)
                    self.Kabob_Routine.jump_to_state_by_name(self.kabob_inventory_state_name)
                else:
                    self.Kabob_Routine.jump_to_state_by_name(self.kabob_pathing_2_state_name)
        else:
            self.Log("Kabob Count Matched - AutoStop")
    
    def HandleStuck(self):  
        try:
            if (Map.IsExplorable() and Party.IsPartyLoaded()):
                if not self.kabob_stuck_timer.IsRunning():
                    self.kabob_stuck_timer.Start()

                currentStep = self.Kabob_Routine.get_current_step_name()

                playerId = Player.GetAgentID()
                localPosition = Player.GetXY()

                if currentStep == self.kabob_waiting_run_state_name and self.stuckPosition:                
                    if not Agent.IsCasting(playerId) and not Agent.IsKnockedDown(playerId) and not Agent.IsMoving(playerId) or (abs(localPosition[0] - self.stuckPosition[0]) <= 20 and abs(localPosition[1] - self.stuckPosition[1]) <= 20):
                        if self.kabob_stuck_timer.HasElapsed(4000):
                            self.player_stuck = True
                            self.kabob_stuck_timer.Reset()
                    else:                    
                        self.kabob_stuck_timer.Stop()
                        self.player_stuck = False

                self.stuckPosition = localPosition
            else:
                self.kabob_stuck_timer.Stop()
                self.kabob_stuck_timer.Reset()
                self.player_stuck = False
        except Exception as e:
            Py4GW.Console.Log("Handle Stuck", f"Error during checking stuck {str(e)}", Py4GW.Console.MessageType.Error)
  
  ### --- ROUTINE FUNCTIONS --- ###

def GetKabobCollected():
    return kabob_Routine.GetKabobCollected()

def GetKabobData():
    return kabob_Routine.GetKabobStats()

kabob_Window = Kabob_Window(bot_name)
kabob_Routine = Kabob_Farm(kabob_Window)

def ApplyLootAndMerchantSelections():
    global kabob_input
    kabob_Routine.ApplySelections(kabob_input, kabob_Window.id_Items, kabob_Window.collect_coins, kabob_Window.collect_events, kabob_Window.collect_items_white, kabob_Window.collect_items_blue, \
                kabob_Window.collect_items_grape, kabob_Window.collect_items_gold, kabob_Window.collect_dye, kabob_Window.sell_items, kabob_Window.sell_items_white, \
                kabob_Window.sell_items_blue, kabob_Window.sell_items_grape, kabob_Window.sell_items_gold, kabob_Window.sell_items_green, kabob_Window.sell_materials, kabob_Window.salvage_items, kabob_Window.salvage_items_white, \
                kabob_Window.salvage_items_blue, kabob_Window.salvage_items_grape, kabob_Window.salvage_items_gold)

def StartBot():
    ApplyLootAndMerchantSelections()
    kabob_Routine.Start()

def StopBot():
    if kabob_Routine.IsBotRunning():
        kabob_Routine.Stop()

def ResetBot():
    # Stop the main state machine  
    kabob_Routine.Stop()
    kabob_Routine.Reset()

def PrintData():
    kabob_Routine.PrintData()

### --- MAIN --- ###
def main():
    try:
        if kabob_Window:
            kabob_Window.Show()

        # Could just put a main timer here and only fire the updates in some interval, but I like more control specific to tasks (eg. Staying Alive, Kill, Loot, etc)
        if Party.IsPartyLoaded():
            if kabob_Routine and kabob_Routine.IsBotRunning():
                kabob_Routine.Update()
                
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