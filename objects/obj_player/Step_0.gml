var _h = keyboard_check(ord("D")) - keyboard_check(ord("A"));
var _v = keyboard_check(ord("S")) - keyboard_check(ord("W"));

if (_h != 0 || _v != 0)
{
	var _len = point_distance(0, 0, _h, _v);
	x += (_h / _len) * move_speed;
	y += (_v / _len) * move_speed * 0.5;
}

if (door_cooldown > 0)
{
	door_cooldown--;
}
else
{
	var _door = instance_place(x, y, obj_door);
	if (_door != noone)
		obj_game.go_through(_door.dir);
}

depth = -y;