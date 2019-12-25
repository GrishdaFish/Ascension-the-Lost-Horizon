import tcod as libtcod


def render_all(game, injected_render_list=None):  # break this up to render ui and other elements separately
    game.gEngine.log_message("In render, becfore clear")
    game.gEngine.console_clear(game.dungeon_console)
    game.gEngine.log_message("Map cleared")
    if game.fov_recompute:
        game.gEngine.log_message("Recomputing fov")
        game.fov_recompute = False
        game.gEngine.map_compute_fov(game.player.x, game.player.y)
        game.gEngine.log_message("Fov computed")
    game.gEngine.log_message("updating lighting...")
    update_lighting(game)
    game.gEngine.log_message("done, drawing map....")
    # self.gEngine.map_draw_fast(self.dungeon_console, self.player.x, self.player.y)
    game.gEngine.map_draw(game.dungeon_console, game.player.x, game.player.y)
    game.gEngine.log_message("done, drawing objects...")
    draw_objects(game)

    # self.world.process()
    game.gEngine.log_message("done... drawing UI...")
    draw_user_interface(game)
    game.gEngine.log_message("done... drawing underplayer")
    player = game.get_names_under_player()
    game.gEngine.log_message("done, flushing messages")
    game.message.flush_messages()
    game.gEngine.log_message("done, rendering barks")
    game.bark_manager.render_barks()
    game.gEngine.log_message("done, perferming injected rendering")
    if injected_render_list:
        for r in injected_render_list:
            r(game)
    game.gEngine.log_message("done, rendering consoles")
    render_consoles(game)
    game.gEngine.log_message("done, rendering complete.")

def update_lighting(game):
    game.gEngine.lightmask_reset()
    game.level.light_handler.update()
    game.level.light_handler.render()
    # r = libtcod.random_get_float(0, -0.025, 0.025)
    # self.gEngine.lightmask_add_light(self.player.x, self.player.y, (0.65 + r))
    game.player.torch.render(game, game.gEngine)
    for object in game.objects:
        if object.fighter:
            r = libtcod.random_get_float(0, -0.025, 0.025)
            game.gEngine.lightmask_add_light(object.x, object.y, (0.4 + r))

    game.gEngine.particle_update(game.level.dungeon)
    game.gEngine.lightmask_compute(game.level.dungeon)


def draw_objects(game):
    game.gEngine.log_message("Drawing objects....")
    for object in game.objects:
        if object.npc:
            game.gEngine.log_message("Drawing NPC...")
            object.draw(game.fov, game.gEngine, force_display=True)
            game.gEngine.log_message("Done")
        if object.misc:
            if object.misc.type == 'up' or object.misc.type == 'down':
                # Draw stairs if they are already found
                if game.gEngine.map_is_explored(object.x, object.y):
                    game.gEngine.log_message("Drawing stairs...")
                    object.draw(game.fov, game.gEngine, force_display=True)
                    game.gEngine.log_message("done..")

            else:
                game.gEngine.log_message("Drawing other misc objects..")
                object.draw(game.fov, game.gEngine)
                game.gEngine.log_message("done")
        else:
            if game.monster_force_display[0] and object.fighter:
                object.draw(game.fov, game.gEngine, force_display=True)
            elif game.loot_force_display[0] and object.item:
                object.draw(game.fov, game.gEngine, force_display=True)
            else:
                object.draw(game.fov, game.gEngine)
    game.gEngine.log_message("Attempting to draw player")
    game.player.draw(game.fov, game.gEngine)
    game.gEngine.log_message("done")


def draw_user_interface(game):
    r, g, b = libtcod.black
    game.gEngine.console_set_default_background(game.panel, r, g, b)
    game.gEngine.console_clear(game.panel)

    game.player_hp_bar.render(1, 1, game.gEngine)
    game.player_torch_bar.render(1, 2, game.gEngine)
    game.player_xp_bar.render(1, 3, game.gEngine)

    r, g, b = libtcod.light_gray
    game.gEngine.console_set_default_foreground(game.panel, r, g, b)
    game.gEngine.console_set_alignment(game.panel, libtcod.LEFT)
    game.gEngine.console_set_default_background(0, r, g, b)
    game.gEngine.console_print(game.panel, 1, 5, "(%dfps) Depth: %d" % (game.gEngine.sys_get_fps(), game.level.depth))
    #game.gEngine.console_print(game.panel, 1, 0, game.get_names_under_mouse())


def render_consoles(game):
    game.hotbar.render()

    game.gEngine.console_blit(game.dungeon_console, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0)
    game.gEngine.console_blit(game.toolbar, 0, 0, game.gEngine.w, 5, 0, 0, game.panel_y - 5, 1.0, 1.0)
    game.gEngine.console_blit(game.panel, 0, 0, game.screen_width, game.panel_height, 0, 0, game.panel_y, 1.0, 1.0)