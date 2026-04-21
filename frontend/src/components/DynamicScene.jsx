import { Canvas, useFrame } from "@react-three/fiber";
import { Environment, Float, Icosahedron, OrbitControls, Stars, Torus } from "@react-three/drei";
import { useRef } from "react";

function Orb({ phase }) {
  const ref = useRef();
  const ringRef = useRef();
  useFrame((_, delta) => {
    if (!ref.current) return;
    ref.current.rotation.x += delta * 0.25;
    ref.current.rotation.y += delta * 0.35;
    if (ringRef.current) {
      ringRef.current.rotation.z += delta * 0.28;
      ringRef.current.rotation.x += delta * 0.08;
    }
  });

  const scale = phase === "interview" ? 1.35 : phase === "report" ? 1.05 : 1.2;
  return (
    <Float speed={phase === "interview" ? 2.8 : 1.8} rotationIntensity={1.8} floatIntensity={2.4}>
      <Icosahedron ref={ref} args={[scale, 1]}>
        <meshStandardMaterial color="#5da6ff" wireframe emissive="#1d6df5" emissiveIntensity={0.9} />
      </Icosahedron>
      <Torus ref={ringRef} args={[scale + 0.35, 0.02, 12, 120]} rotation={[Math.PI / 3, 0, 0]}>
        <meshStandardMaterial color={phase === "report" ? "#7ed4ff" : "#9b7cff"} emissive="#4f9cff" emissiveIntensity={0.8} />
      </Torus>
    </Float>
  );
}

export default function DynamicScene({ phase }) {
  return (
    <div className="scene-wrap" aria-hidden="true">
      <Canvas camera={{ position: [0, 0, 4], fov: 50 }}>
        <ambientLight intensity={0.55} />
        <pointLight position={[3, 3, 2]} intensity={2.8} color="#6db7ff" />
        <pointLight position={[-4, -3, -2]} intensity={1.8} color="#9b7cff" />
        <Stars radius={90} depth={55} count={phase === "setup" ? 1800 : 2600} factor={3.5} saturation={0} fade speed={0.9} />
        <Environment preset="night" />
        <Orb phase={phase} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.9} />
      </Canvas>
    </div>
  );
}

