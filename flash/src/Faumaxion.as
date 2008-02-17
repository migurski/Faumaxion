package {
	
	import com.teczno.faumaxion.Location;
	import com.teczno.faumaxion.Map;
	
	import flash.display.Sprite;
	import flash.display.StageAlign;
	import flash.display.StageScaleMode;

	public class Faumaxion extends Sprite
	{
		public function Faumaxion()
		{
			stage.align = StageAlign.TOP_LEFT;
			stage.scaleMode = StageScaleMode.NO_SCALE;
			
			var map:Map = new Map(new Location(40, -120), 512);
			addChild(map);
		}
	}
}
