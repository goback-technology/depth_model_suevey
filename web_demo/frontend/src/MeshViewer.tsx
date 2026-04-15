import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";

type MeshData = {
  vertices: [number, number, number][];
  faces: [number, number, number][];
};

type Props = {
  voxels: [number, number, number][];
  voxelSize: number;
  mesh: MeshData | null;
  showVoxels: boolean;
  showMesh: boolean;
};

function VoxelCloud({ points, voxelSize }: { points: [number, number, number][]; voxelSize: number }) {
  const ref = useRef<THREE.InstancedMesh>(null);
  const maxPoints = 20000;
  const renderPoints = points.length > maxPoints ? points.slice(0, maxPoints) : points;

  const matrixArray = useMemo(() => {
    const mat = new THREE.Matrix4();
    return renderPoints.map((p) => {
      mat.makeTranslation(p[0], p[1], p[2]);
      return mat.clone();
    });
  }, [renderPoints]);

  useEffect(() => {
    const mesh = ref.current;
    if (!mesh) {
      return;
    }
    matrixArray.forEach((m, i) => mesh.setMatrixAt(i, m));
    mesh.instanceMatrix.needsUpdate = true;
  }, [matrixArray]);

  return (
    <instancedMesh ref={ref} args={[undefined, undefined, matrixArray.length]}>
      <boxGeometry args={[voxelSize, voxelSize, voxelSize]} />
      <meshStandardMaterial color="#ef8354" roughness={0.65} metalness={0.1} />
    </instancedMesh>
  );
}

function SurfaceMesh({ mesh }: { mesh: MeshData }) {
  const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry();
    const vertices = new Float32Array(mesh.vertices.flat());
    const indices = new Uint32Array(mesh.faces.flat());
    g.setAttribute("position", new THREE.BufferAttribute(vertices, 3));
    g.setIndex(new THREE.BufferAttribute(indices, 1));
    g.computeVertexNormals();
    return g;
  }, [mesh]);

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial color="#4f5d75" wireframe={false} transparent opacity={0.85} />
    </mesh>
  );
}

export default function MeshViewer({ voxels, voxelSize, mesh, showVoxels, showMesh }: Props) {
  return (
    <div className="viewer-wrap">
      <Canvas camera={{ position: [0.5, 0.5, 1.6], fov: 50 }}>
        <color attach="background" args={["#f6f8fb"]} />
        <ambientLight intensity={0.8} />
        <directionalLight position={[3, 3, 3]} intensity={0.9} />
        <group rotation={[-Math.PI / 2, 0, 0]}>
          {showVoxels ? <VoxelCloud points={voxels} voxelSize={voxelSize} /> : null}
          {showMesh && mesh ? <SurfaceMesh mesh={mesh} /> : null}
        </group>
        <OrbitControls makeDefault />
      </Canvas>
    </div>
  );
}
