package com.teczno.faumaxion.icosahedron
{
	import com.teczno.faumaxion.mesh.*;
	
	public class World
	{
		private static var FACES:Array;
		
		public static function faces():Array
		{
			if(FACES)
				return FACES;

			// Cartesian coordinates for the 12 vertices of icosahedron
			var vertices:Object = { 1: new Vertex( 0.420152426708710003,  0.078145249402782959,  0.904082550615019298),
			                        2: new Vertex( 0.995009439436241649, -0.091347795276427931,  0.040147175877166645),
			                        3: new Vertex( 0.518836730327364437,  0.835420380378235850,  0.181331837557262454),
			                        4: new Vertex(-0.414682225320335218,  0.655962405434800777,  0.630675807891475371),
			                        5: new Vertex(-0.515455959944041808, -0.381716898287133011,  0.767200992517747538),
			                        6: new Vertex( 0.355781402532944713, -0.843580002466178147,  0.402234226602925571),
			                        7: new Vertex( 0.414682225320335218, -0.655962405434800777, -0.630675807891475371),
			                        8: new Vertex( 0.515455959944041808,  0.381716898287133011, -0.767200992517747538),
			                        9: new Vertex(-0.355781402532944713,  0.843580002466178147, -0.402234226602925571),
			                       10: new Vertex(-0.995009439436241649,  0.091347795276427931, -0.040147175877166645),
			                       11: new Vertex(-0.518836730327364437, -0.835420380378235850, -0.181331837557262454),
			                       12: new Vertex(-0.420152426708710003, -0.078145249402782959, -0.904082550615019298)};
			
			var edges:Object = {};
			var faces:Object = {};
			
			var edgeKinds:Object = {}; 

			edgeKinds['1,2'] = 'LAND';
			edgeKinds['2,3'] = 'LAND';
			edgeKinds['1,3'] = 'LAND';

			edgeKinds['1,4'] = 'LAND';
			edgeKinds['3,4'] = 'LAND';

			edgeKinds['1,5'] = 'LAND';
			edgeKinds['4,5'] = 'LAND';

			edgeKinds['1,6'] = 'WATER';
			edgeKinds['5,6'] = 'LAND';
			
			edgeKinds['2,6'] = 'WATER';

			edgeKinds['2,8'] = 'WATER';
			edgeKinds['3,8'] = 'WATER';

			edgeKinds['3,9'] = 'WATER';
			edgeKinds['8,9'] = 'WATER';
			
			edgeKinds['4,9'] = 'LAND';
			
			edgeKinds['4,10'] = 'LAND';
			edgeKinds['9,10'] = 'LAND';

			edgeKinds['5,10'] = 'WATER';

			edgeKinds['5,11'] = 'WATER';
			edgeKinds['10,11'] = 'WATER';
			
			edgeKinds['6,11'] = 'LAND';
			
			edgeKinds['6,7'] = 'LAND';
			edgeKinds['7,11'] = 'LAND';
			
			edgeKinds['2,7'] = 'WATER';
			
			edgeKinds['7,8'] = 'WATER';
			
			edgeKinds['8,12'] = 'LAND';
			edgeKinds['9,12'] = 'LAND';
			
			edgeKinds['10,12'] = 'WATER';
			
			edgeKinds['11,12'] = 'WATER';
			
			edgeKinds['7,12'] = 'WATER';
			
			for each(var tv1v2:Array in [['01', 1, 3], ['01', 3, 2], ['01', 2, 1], ['02', 1, 4], ['02', 4, 3], ['02', 3, 1], ['03', 1, 5], ['03', 5, 4], ['03', 4, 1], ['04', 1, 6], ['04', 6, 5], ['04', 5, 1], ['05', 1, 2], ['05', 2, 6], ['05', 6, 1], ['06', 2, 3], ['06', 3, 8], ['06', 8, 2], ['07', 3, 9], ['07', 9, 8], ['07', 8, 3], ['08', 3, 4], ['08', 4, 9], ['08', 9, 3], ['09', 4, 10], ['09', 10, 9], ['09', 9, 4], ['10', 4, 5], ['10', 5, 10], ['10', 10, 4], ['11', 5, 11], ['11', 11, 10], ['11', 10, 5], ['12', 5, 6], ['12', 6, 11], ['12', 11, 5], ['13', 6, 7], ['13', 7, 11], ['13', 11, 6], ['14', 2, 7], ['14', 7, 6], ['14', 6, 2], ['15', 2, 8], ['15', 8, 7], ['15', 7, 2], ['16', 8, 9], ['16', 9, 12], ['16', 12, 8], ['17', 9, 10], ['17', 10, 12], ['17', 12, 9], ['18', 10, 11], ['18', 11, 12], ['18', 12, 10], ['19', 11, 7], ['19', 7, 12], ['19', 12, 11], ['20', 8, 12], ['20', 12, 7], ['20', 7, 8]]) {
				var t:String = tv1v2[0] as String;
				var v1:int = tv1v2[1] as int;
				var v2:int = tv1v2[2] as int;
				
				// assign a face
				var face:Face = faces[t] as Face;
				
				if(!face) {
					face = faces[t] = new Face(null, null, null, t);
				}
					
				var edgeKey:String = Math.min(v1, v2).toString() + ',' + Math.max(v1, v2).toString();
				
				// this edge has two vertices
				var vertexA:Vertex = vertices[v1];
				var vertexB:Vertex = vertices[v2];
				
				// see if the edge already exists in the opposite direction
				var edge:Edge = edges[edgeKey] as Edge;
				
				if(edge) {
					// edge exists, so assign it the appropriate face
					edge.triangleB = face;

				} else {
					// new edge, just one face for now
					var kind:String = edgeKinds[edgeKey] as String;
					edge = new Edge(vertexA, vertexB, face, null, kind);
					edges[edgeKey] = edge;
				}
				
				if(face.edgeA == null) {
					face.edgeA = edge;

				} else if(face.edgeB == null) {
					face.edgeB = edge;
					
				} else if(face.edgeC == null) {
					face.edgeC = edge;
				}
				
				face.calculateCenter();
			}
			
			FACES = [];
			
			for each(face in faces) {
				FACES.push(face);
			}
			
			return FACES;
		}
	}
}