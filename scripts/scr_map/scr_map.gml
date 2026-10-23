function map_generate(_target_count)
{
	var _room_count = 1;
	var _rooms = {};
	var _directions = [
		["n",0,-1,"s"],
		["e",1,0,"w"],
		["s",0,1,"n"],
		["w",-1,0,"e"]
	];
	
	_rooms[$ "0,0"] = map_new_node(0, 0, "start");
	
	while (_room_count < _target_count)
	{
		var _existing_rooms = variable_struct_get_names(_rooms);
		var _parent_room = _rooms[$ _existing_rooms[irandom(array_length(_existing_rooms) -1)]];
		
		var _direction = _directions[irandom(3)];
		var _nx = _parent_room.gx + _direction[1];
		var _ny = _parent_room.gy + _direction[2];
		var _new_room = string(_nx) + "," + string(_ny);
		
		if (!variable_struct_exists(_rooms, _new_room))
		{
			_rooms[$ _new_room] = map_new_node(_nx, _ny, "normal");	
			_rooms[$ _new_room].doors[$ _direction[3]] = true;
			
			_parent_room.doors[$ _direction[0]] = true;
			
			_room_count++;
		}
	}
	
	var _existing_rooms = variable_struct_get_names(_rooms);
	for (var i = 0; i < array_length(_existing_rooms); i++)
	{
		var _room = _rooms[$ _existing_rooms[i]];
		var _room_doors = _room.doors.n + _room.doors.e + _room.doors.s + _room.doors.w;
		if (_room_doors == 1 && _room.type != "start")
			_room.type = "end";
		_room.template = map_pick_template(_room);
	}
	
	return _rooms;
}

function map_new_node(_gx, _gy, _type)
{
	return 
	{ 
		gx: _gx,
		gy: _gy, 
		type: _type, 
		template: noone, 
		doors: 
		{ 
			n: false, 
			e: false, 
			s: false, 
			w: false 
		} 
	};
}

function map_pick_template(_room)
{
	var _tag = "start";
	if (_room.type == "normal") _tag = choose("house", "yard");
	
	var _pool = tag_get_asset_ids(_tag, asset_room);
	return _pool[irandom(array_length(_pool) - 1)];
}

function scr_map(){

}