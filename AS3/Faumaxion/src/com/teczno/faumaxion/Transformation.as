package com.teczno.faumaxion
{
	import flash.geom.Matrix;
	import flash.geom.Point;
	
	public class Transformation
	{
		private var ax:Number;
		private var bx:Number;
		private var cx:Number;
		private var ay:Number;
		private var by:Number;
		private var cy:Number;
		
		public function Transformation(ax:Number, bx:Number, cx:Number, ay:Number, by:Number, cy:Number)
		{
			this.ax = ax;
			this.bx = bx;
			this.cx = cx;
			this.ay = ay;
			this.by = by;
			this.cy = cy;
		}
		
		public function apply(p:Point):Point
		{
			return new Point(ax * p.x + bx * p.y + cx,
			                 ay * p.x + by * p.y + cy);
		}
		
		public function unapply(p:Point):Point
		{
			return new Point((p.x * by - p.y * bx - cx * by + cy * bx) / (ax * by - ay * bx),
			                 (p.x * ay - p.y * ax - cx * ay + cy * ax) / (bx * ay - by * ax));
		}
		
		public function multiply(other:Transformation):Transformation
		{
			var nax:Number = (other.ax * ax + other.bx * ay)
			var nbx:Number = (other.ax * bx + other.bx * by)
			var ncx:Number = (other.ax * cx + other.bx * cy + other.cx)
			
			var nay:Number = (other.ay * ax + other.by * ay)
			var nby:Number = (other.ay * bx + other.by * by)
			var ncy:Number = (other.ay * cx + other.by * cy + other.cy)
			
			return new Transformation(nax, nbx, ncx, nay, nby, ncy);
		}
		
		public function matrix():Matrix
		{
			return new Matrix(ax, ay, bx, by, cx, cy);
		}
		
		public static function deriveTransformation(a1:Point, a2:Point, b1:Point, b2:Point, c1:Point, c2:Point):Transformation
		{
			var abcx:Array = linearSolution(a1.x, a1.y, a2.x, b1.x, b1.y, b2.x, c1.x, c1.y, c2.x);
			var abcy:Array = linearSolution(a1.x, a1.y, a2.y, b1.x, b1.y, b2.y, c1.x, c1.y, c2.y);
			
			
			return new Transformation(abcx[0] as Number, abcx[1] as Number, abcx[2] as Number, abcy[0] as Number, abcy[1] as Number, abcy[2] as Number);
		}
		
		public static function linearSolution(r1:Number, s1:Number, t1:Number, r2:Number, s2:Number, t2:Number, r3:Number, s3:Number, t3:Number):Array
		{
			var a:Number = (((t2 - t3) * (s1 - s2)) - ((t1 - t2) * (s2 - s3)))
			             / (((r2 - r3) * (s1 - s2)) - ((r1 - r2) * (s2 - s3)));
			
			var b:Number = (((t2 - t3) * (r1 - r2)) - ((t1 - t2) * (r2 - r3)))
			             / (((s2 - s3) * (r1 - r2)) - ((s1 - s2) * (r2 - r3)));
			
			var c:Number = t1 - (r1 * a) - (s1 * b);
			
			return [a, b, c];
		}
	}
}
