import tcod as libtcod


def render_all(game, injected_render_list=None):  # break this up to render ui and other elements separately
    if game.game_state == 'playing':
        game.gEngine.console_clear(game.dungeon_console)
        if game.fov_recompute:
            game.fov_recompute = False
            game.gEngine.map_compute_fov(game.player.x, game.player.y)

        game.gEngine.particle_update()
        update_lighting(game)

        game.gEngine.map_draw(game.dungeon_console, game.player.x, game.player.y)

        game.gEngine.particle_draw(game.dungeon_console) # TODO: Add additional Particle array for character particles

        game.gEngine.map_blit(game.dungeon_console)

        game.gEngine.particle_draw(game.dungeon_console) # TODO: Add additional Particle array for character particles

        game.gEngine.animation_draw_animations_back()

        draw_objects(game)

        game.gEngine.animation_draw_animations_fore()

    draw_user_interface(game)
    player = game.get_names_under_player()
    game.message.flush_messages()
    game.bark_manager.render_barks()

    if game.game_state == 'playing':
        if injected_render_list:
            for r in injected_render_list:
                r(game)

    elif game.game_state == 'dead':
        game.gEngine.animation_draw_animation("death arrow", game.dungeon_console, 0, 0)
        # game.gEngine.console_clear(0)
        # game.gEngine.console_clear(game.death_console)
        # draw death screen animation
        # game.death_index += 1
        # if not game.death_index > len(game.death_animation) - 1:
        #     img = game.death_animation[game.death_index]
        #
        # else:
        #     img = game.death_animation[len(game.death_animation)-1]
        # game.gEngine.image_blit_2x(img, game.dungeon_console, 0, 0)
        # game.gEngine.console_blit(game.death_console, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0)

        # game.gEngine.console_flush()

    render_consoles(game)

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
    for object in game.objects:
        if object.npc:
            object.draw(game.fov, game.gEngine, force_display=True)
        if object.misc:
            if object.misc.type == 'up' or object.misc.type == 'down':
                # Draw stairs if they are already found
                if game.gEngine.map_is_explored(object.x, object.y):
                    object.draw(game.fov, game.gEngine, force_display=False)

            else:
                object.draw(game.fov, game.gEngine)
        else:
            if game.monster_force_display[0] and object.fighter:
                object.draw(game.fov, game.gEngine, force_display=True)
            elif game.loot_force_display[0] and object.item:
                object.draw(game.fov, game.gEngine, force_display=True)
            else:
                object.draw(game.fov, game.gEngine)
    game.player.draw(game.fov, game.gEngine)



def draw_user_interface(game):
    game.gEngine.animation_draw_ui()

    col = libtcod.black
    game.gEngine.console_set_default_background(game.panel, col)
    game.gEngine.console_clear(game.panel)

    game.player_hp_bar.render(1, 1, [game.player.fighter.hp, game.player.fighter.stat.get_stat_base("HP")], 'Hp: ')
    game.player_resource_bar.render(1, 2,[game.player.fighter.stamina, game.player.fighter.stat.get_stat_base("Stamina")], "Stamina: ")
    game.player_xp_bar.render(1, 3,  [game.player.fighter.current_xp, game.player.fighter.xp_to_next_level], 'Xp: ')

    if game.player.fighter.gear.light_source:
        current = game.player.fighter.gear.light_source.item.equipment.fuel
        max = game.player.fighter.gear.light_source.item.equipment.max_fuel
        data = [current, max]
    else:
        data = [0, 0]
    game.player_torch_bar.update(data)

    col = libtcod.light_gray
    game.gEngine.console_set_default_foreground(game.panel, col)
    game.gEngine.console_set_alignment(game.panel, libtcod.LEFT)
    game.gEngine.console_set_default_background(0, col)
    #game.gEngine.console_print(game.panel, 1, 7, "(%dfps) Depth: %d" % (game.gEngine.sys_get_fps(), game.level.depth))
    #game.gEngine.console_print(game.panel, 1, 0, game.get_names_under_mouse())


def render_consoles(game):
    game.hotbar.render()
    #if game.game_state == 'playing':
    game.gEngine.console_blit(game.dungeon_console, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0)
    game.gEngine.console_blit(game.toolbar, 0, 0, game.gEngine.w, 5, 0, 0, game.panel_y - 5, 1.0, 1.0)
    game.gEngine.console_blit(game.panel, 0, 0, game.screen_width, game.panel_height, 0, 0, game.panel_y, 1.0, 1.0)
