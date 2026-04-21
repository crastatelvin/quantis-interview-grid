import { useEffect, useRef } from "react";
import * as THREE from "three";

export default function HoloAvatar({ speaking, size = 110 }) {
  const ref = useRef(null);

  useEffect(() => {
    const mount = ref.current;
    if (!mount) return;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(70, 1, 0.1, 1000);
    camera.position.z = 3;
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(size, size);
    mount.appendChild(renderer.domElement);

    const mesh = new THREE.Mesh(
      new THREE.IcosahedronGeometry(1, 1),
      new THREE.MeshBasicMaterial({ color: 0x1d6df5, wireframe: true, transparent: true, opacity: 0.75 })
    );
    scene.add(mesh);
    let t = 0;
    let id;
    const loop = () => {
      t += 0.01;
      mesh.rotation.x += 0.004;
      mesh.rotation.y += 0.007;
      const s = speaking ? 1 + Math.sin(t * 8) * 0.06 : 1 + Math.sin(t * 2) * 0.02;
      mesh.scale.set(s, s, s);
      renderer.render(scene, camera);
      id = requestAnimationFrame(loop);
    };
    loop();
    return () => {
      cancelAnimationFrame(id);
      mount.removeChild(renderer.domElement);
      renderer.dispose();
    };
  }, [size, speaking]);

  return <div ref={ref} style={{ width: size, height: size }} />;
}

