package com.teczno.faumaxion
{
	import com.teczno.faumaxion.icosahedron.Face;
	
	import flash.display.Loader;
	import flash.display.Shape;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.IOErrorEvent;
	import flash.geom.Point;
	import flash.net.URLRequest;

	public class Tile extends Sprite
	{
		public var url:URLRequest;
		
		private var face:Face;
		private var direction:String;
		private var loader:Loader;
		
		public static const UP:String = 'triangle points up';
		public static const DOWN:String = 'triangle points down';
		
		public function Tile(face:Face, url:URLRequest, direction:String)
		{
			this.face = face;
			this.url = url;
			this.direction = direction;
			
			addEventListener(Event.ADDED_TO_STAGE, onAddedToStage);
		}
		
		public function onAddedToStage(e:Event):void
		{
			var corners:Array = cornerPoints();
			var i1:Point = corners[0] as Point;
			var i2:Point = corners[1] as Point;
			var i3:Point = corners[2] as Point;

			graphics.beginFill(0x000033, .35);
			graphics.moveTo(i1.x, i1.y);
			graphics.lineTo(i2.x, i2.y);
			graphics.lineTo(i3.x, i3.y);
			graphics.lineTo(i1.x, i1.y);
			graphics.endFill();

			var tileMask:Shape = new Shape();
			tileMask.graphics.beginFill(0xFF00FF);
			tileMask.graphics.moveTo(i1.x, i1.y);
			tileMask.graphics.lineTo(i2.x, i2.y);
			tileMask.graphics.lineTo(i3.x, i3.y);
			tileMask.graphics.lineTo(i1.x, i1.y);
			tileMask.graphics.endFill();
			addChild(tileMask);

			loader = new Loader();
			loader.contentLoaderInfo.addEventListener(IOErrorEvent.IO_ERROR, onLoadError);

			loader.load(url);
			loader.mask = tileMask;

			addChild(loader);
			addEventListener(Event.REMOVED_FROM_STAGE, onRemovedFromStage);
		}
		
		public function onRemovedFromStage(e:Event):void
		{
			try {
				loader.close();
			} catch(e:Error) {
				// who cares
			}
		}
		
		public function cornerPoints():Array
		{
			var i1:Point, i2:Point, i3:Point;
			
			if(direction == UP) {
				i1 = new Point(Face.SIDE/2, Face.SIDE - Face.SIDE * Math.sin(Math.PI/3));
				i2 = new Point(Face.SIDE, Face.SIDE);
				i3 = new Point(0, Face.SIDE);

			} else if(direction == DOWN) {
				i1 = new Point(Face.SIDE/2, Face.SIDE * Math.sin(Math.PI/3));
				i2 = new Point(0, 0);
				i3 = new Point(Face.SIDE, 0);
			}
			
			return [i1, i2, i3];
		}
		
		public function onLoadError(e:Event):void
		{
			// don't care
		}
	}
}