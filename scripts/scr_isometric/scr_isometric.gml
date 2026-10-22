#macro TILE_W 64
#macro TILE_H 32

function iso_to_screen(_gx, _gy)
{
	return 
	{
		x: (_gx - _gy) * (TILE_W / 2),
		y: (_gx + _gy) * (TILE_H / 2)
	};
}

function screen_to_iso(_sx, _sy)
{
	return
	{
		gx: (_sx / (TILE_W / 2) + _sy / (TILE_H / 2)) / 2,
		gy: (_sy / (TILE_H / 2) - _sx / (TILE_W / 2)) / 2,
	};
}

function scr_isometric(){

}