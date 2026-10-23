with (obj_door)
{
	if (!other.current.doors[$ dir])
		instance_destroy();
}

var _spawn_x = room_width / 2;
var _spawn_y = room_height / 2;

with (obj_door)
{
	if (dir == other.entry_direction)
	{
		_spawn_x = x;
		_spawn_y = y;
	}
}

var _player = instance_create_depth(_spawn_x, _spawn_y, 0, obj_player);
_player.door_cooldown = 200;