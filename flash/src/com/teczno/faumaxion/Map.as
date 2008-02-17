package com.teczno.faumaxion
{
	import com.teczno.faumaxion.icosahedron.Face;
	import com.teczno.faumaxion.icosahedron.World;
	import com.teczno.faumaxion.mesh.*;
	
	import flash.display.Loader;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.KeyboardEvent;
	import flash.events.MouseEvent;
	import flash.geom.Point;
	import flash.net.URLRequest;

	public class Map extends Sprite
	{
		private var center:Location;
		private var zoom:Number;
		
		public function Map(center:Location, zoom:Number)
		{
			this.center = center;
			this.zoom = zoom;
			
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
				zoom *= .5;
				init();
				
			} else if(e.charCode == 0x3D) {
				// "=" zoom in
				zoom /= .5;
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
			while(numChildren)
				removeChildAt(0);
				
			var start:Face = Face.vertexFace(Face.locationVertex(center));
			
			start.reset();
			start.orientNorth(center);
			start.centerOn(center);
			
			start.scale(zoom);
			start.translate(stage.stageWidth/2, stage.stageHeight/2);
			
			for each(var face:Face in start.arrangeNeighbors('LAND')) {
				applyFace([face.path], face, 'UP');
				continue;
				
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
			}
		}
		
		public function faceOnStage(corners:Array, face:Face):Boolean
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
		
		public function applyFace(srcPath:Array, face:Face, point:String, corners:Array=null):void
		{
			if(!corners) {
				corners = [];

				for each(var vertex:Vertex in face.vertices()) {
					corners.push(face.projectVertex(vertex));
				}
			}
			
			if(!faceOnStage(corners, face))
				return;
			
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
					var nextSrcPath:Array = srcPath.slice();
					nextSrcPath.push(p);
					
					if(p == 'k') {
						applyFace(nextSrcPath, face, (point == 'UP' ? 'DOWN' : 'UP'), subcorners[p] as Array);

					} else {
						applyFace(nextSrcPath, face, point, subcorners[p] as Array);
					}
				}
				
				return;
			}
			
			var i1:Point, i2:Point, i3:Point;
			
			if(point == 'UP') {
				i1 = new Point(Face.SIDE/2, Face.SIDE - Face.SIDE * Math.sin(Math.PI/3));
				i2 = new Point(Face.SIDE, Face.SIDE);
				i3 = new Point(0, Face.SIDE);

			} else if(point == 'DOWN') {
				i1 = new Point(Face.SIDE/2, Face.SIDE * Math.sin(Math.PI/3));
				i2 = new Point(0, 0);
				i3 = new Point(Face.SIDE, 0);
			}
			
			var loader:Loader = new Loader();
			
			var t:Transformation = Transformation.deriveTransformation(i1, f1, i2, f2, i3, f3);
			loader.transform.matrix = t.matrix();

			loader.load(new URLRequest('http://faumaxion.modestmaps.com/' + srcPath.join('/') + '.png'));
			addChild(loader);
		}
	}
}