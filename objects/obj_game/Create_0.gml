randomize();
map = map_generate(10);
current = map[$ "0,0"];
entry_direction = "";

go_through = function(_direction)
{
	var _off = { n: [0,-1], e: [1,0], s: [0,1], w: [-1,0] };
	var _opp = { n: "s", e: "w", s: "n", w: "e" };
	
	var _room = string(current.gx + _off[$ _direction][0]) + "," + string(current.gy + _off[$ _direction][1]);
	
	current = map[$ _room];
	entry_direction = _opp[$ _direction]
	
	room_goto(current.template);
}

room_goto(current.template);