package com.teczno.faumaxion
{
	import com.teczno.faumaxion.icosahedron.Face;
	import com.teczno.faumaxion.icosahedron.World;
	import com.teczno.faumaxion.mesh.*;
	
	import flash.display.DisplayObject;
	import flash.display.Loader;
	import flash.display.Shape;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.KeyboardEvent;
	import flash.events.MouseEvent;
	import flash.geom.Matrix;
	import flash.geom.Point;
	import flash.net.URLRequest;
	import flash.utils.Dictionary;

	public class Map extends Sprite
	{
		private var center:Location;
		private var zoom:Number;
		private var tiles:Dictionary;
		
		public function Map(center:Location, zoom:Number)
		{
			this.center = center;
			this.zoom = zoom;
			this.tiles = new Dictionary();
			
			addEventListener(Event.ADDED_TO_STAGE, onAddedToStage);
		}
		
		public function onClicked(e:MouseEvent):void
		{
			var point:Point = new Point(e.stageX, e.stageY);
			globalToLocal(point);
			trace(point + ' --> ' + pointLocation(point));
			
			center = pointLocation(point);
			init();
		}
		
		public function onKeyPressed(e:KeyboardEvent):void
		{
			if(e.charCode == 0x2D) {
				// "-" zoom out
				zoom /= Math.sqrt(2);
				zoom = Math.max(32, zoom);
				init();
				
			} else if(e.charCode == 0x3D) {
				// "=" zoom in
				zoom *= Math.sqrt(2);
				zoom = Math.min(4096, zoom);
				init();
			}
		}
		
		public function pointFace(point:Point):Face
		{
			var face:Face;
			var distances:Array = [];
			
			for each(face in World.faces()) {
				distances.push({distance: Point.distance(point, face.projectVertex(face.center)), face: face});
			}
			
			distances.sortOn('distance', Array.NUMERIC);
			
			return distances[0]['face'] as Face;
		}
		
		public function pointLocation(point:Point):Location
		{
			return pointFace(point).unprojectPoint(point);
		}
		
		public function onAddedToStage(e:Event):void
		{
			init();
		}
		
		public function init():void
		{
			trace('init(), center: ' + center + ', zoom: ' + zoom);
			
			var start:Face = Face.vertexFace(Face.locationVertex(center));
			
			start.reset();
			start.orientNorth(center);
			start.centerOn(center);
			
			start.scale(zoom);
			start.translate(stage.stageWidth/2, stage.stageHeight/2);
			
			var applied:Array = [];
			
			for each(var face:Face in start.arrangeNeighbors('LAND')) {
				applied = applied.concat(applyFace(face.path, face, Tile.UP));
				
				/*
				for each(var edge:Edge in face.edges()) {
					var p1:Point = face.projectVertex(edge.vertexA);
					var p2:Point = face.projectVertex(edge.vertexB);
					
					if(edge.kind == 'LAND') {
						graphics.lineStyle(2, 0x00CC00);

					} else if(edge.kind == 'WATER') {
						graphics.lineStyle(2, 0x0066FF);
					}

					graphics.moveTo(p1.x, p1.y);
					graphics.lineTo(p2.x, p2.y);
					graphics.lineStyle();
				}
				*/
			}

			// remove any tiles that were not part of this application process
			for(var srcPath:String in tiles) {
				var tile:Tile = tiles[srcPath] as Tile;

				if(tile && applied.indexOf(tile) == -1) {
					removeChild(tile);
					delete tiles[srcPath];
				}
			}
		}
		
		public function isFaceOnStage(corners:Array, face:Face):Boolean
		{
			var f1:Point = corners[0] as Point;
			var f2:Point = corners[1] as Point;
			var f3:Point = corners[2] as Point;
			
			var fxmin:Number = Math.min(f1.x, f2.x, f3.x);
			var fxmax:Number = Math.max(f1.x, f2.x, f3.x);
			var fymin:Number = Math.min(f1.y, f2.y, f3.y);
			var fymax:Number = Math.max(f1.y, f2.y, f3.y);
			
			if(fxmin >= 0 && fymin >= 0 && fxmax <= stage.stageWidth && fymax <= stage.stageHeight) {
				// simple bbox check: face is certainly visible
				return true;
				
			} else if(fxmax <= 0 || fymax <= 0 || fxmin >= stage.stageWidth || fymin >= stage.stageHeight) {
				// simple bbox check: face is certainly not visible
				return false;
				
			} else {
				// face *may* not be visible... assume it is for now
				return true;
			}
		}
		
		private function applyFace(srcPath:String, face:Face, direction:String, corners:Array=null):Array
		{
			if(!corners) {
				corners = [];

				for each(var vertex:Vertex in face.vertices()) {
					corners.push(face.projectVertex(vertex));
				}
			}

			if(!isFaceOnStage(corners, face))
				return [];
			
			var applied:Array = [];
			
			var f1:Point = corners[0] as Point;
			var f2:Point = corners[1] as Point;
			var f3:Point = corners[2] as Point;
			
			// magnification factor of current face image.
			var side:Point = new Point(f2.x - f3.x, f2.y - f3.y);
			var magnify:Number = Math.sqrt(side.x * side.x + side.y * side.y) / Face.SIDE;
			
			if(magnify > 1.4) {
				// split each side in half
				var f12:Point = new Point((f1.x + f2.x)/2, (f1.y + f2.y)/2);
				var f23:Point = new Point((f2.x + f3.x)/2, (f2.y + f3.y)/2);
				var f31:Point = new Point((f3.x + f1.x)/2, (f3.y + f1.y)/2);
				
				var subcorners:Object = {i: [f1, f12, f31],
				                         l: [f12, f2, f23],
				                         j: [f31, f23, f3],
				                         k: [f23, f31, f12]};
				
				for(var p:String in subcorners) {
					if(p == 'k') {
						applied = applied.concat(applyFace(srcPath+'/'+p, face, (direction == Tile.UP ? Tile.DOWN : Tile.UP), subcorners[p] as Array));

					} else {
						applied = applied.concat(applyFace(srcPath+'/'+p, face, direction, subcorners[p] as Array));
					}
				}
				
				return applied;
			}
			
			var tile:Tile = tiles[srcPath] as Tile;
			
			if(!tile) {
				// if one does not already exist...
				tile = new Tile(face, new URLRequest('http://faumaxion.modestmaps.com/' + srcPath + '.jpg'), direction);
				tiles[srcPath] = tile;
				addChild(tile);
			}
			
			var corners:Array = tile.cornerPoints();
			tile.transform.matrix = Transformation.deriveTransformation(corners[0] as Point, f1, corners[1] as Point, f2, corners[2] as Point, f3).matrix();

			return [tile];
		}
	}
}