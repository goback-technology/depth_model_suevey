import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import MeshViewer from "./MeshViewer";
import { createJob, getBackendVersion, getJob, getMesh, getVoxels } from "./api";

declare const __APP_VERSION__: string;

type MeshData = {
  vertices: [number, number, number][];
  faces: [number, number, number][];
};

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [voxels, setVoxels] = useState<[number, number, number][]>([]);
  const [voxelSize, setVoxelSize] = useState(0.03);
  const [mesh, setMesh] = useState<MeshData | null>(null);
  const [model, setModel] = useState<"Small" | "Base" | "Large">("Small");
  const [meshMethod, setMeshMethod] = useState<"poisson" | "bpa">("poisson");
  const [depthTrunc, setDepthTrunc] = useState(2.2);
  const [showVoxels, setShowVoxels] = useState(true);
  const [showMesh, setShowMesh] = useState(true);

  const backendVersionQuery = useQuery({
    queryKey: ["backendVersion"],
    queryFn: getBackendVersion,
    staleTime: Infinity,
    retry: 1,
  });

  const createJobMutation = useMutation({
    mutationFn: async () => {
      if (!file) {
        throw new Error("이미지를 선택하세요");
      }
      return createJob({
        image: file,
        model,
        meshMethod,
        voxelSize,
        depthTrunc,
      });
    },
    onSuccess: (res) => {
      setJobId(res.job_id);
      setVoxels([]);
      setMesh(null);
    }
  });

  const jobQuery = useQuery({
    queryKey: ["job", jobId],
    queryFn: async () => getJob(jobId as string),
    enabled: Boolean(jobId),
    refetchInterval: (q) => {
      const status = q.state.data?.status;
      if (!status || status === "queued" || status === "running") {
        return 1500;
      }
      return false;
    }
  });

  const isProcessing =
    createJobMutation.isPending ||
    jobQuery.data?.status === "queued" ||
    jobQuery.data?.status === "running";

  useEffect(() => {
    const loadArtifacts = async () => {
      const job = jobQuery.data;
      if (!job || job.status !== "done") {
        return;
      }
      if (!job.artifacts.voxels_url || !job.artifacts.mesh_url) {
        return;
      }
      const voxelsData = await getVoxels(job.artifacts.voxels_url);
      const meshData = await getMesh(job.artifacts.mesh_url);
      setVoxelSize(voxelsData.voxel_size);
      setVoxels(voxelsData.points);
      setMesh(meshData);
    };

    loadArtifacts().catch(() => {
      setVoxels([]);
      setMesh(null);
    });
  }, [jobQuery.data]);

  return (
    <main className="page">
      <header className="panel">
        <div className="title-row">
          <h1>Depth to Voxel Web Demo</h1>
          <div className="version-group">
            <span className="version-chip">FE v{__APP_VERSION__}</span>
            <span className="version-chip">
              BE {backendVersionQuery.data ? `v${backendVersionQuery.data}` : backendVersionQuery.isError ? "연결 실패" : "…"}
            </span>
          </div>
        </div>
        <p>이미지를 업로드하면 깊이 추정 후 복셀과 메시를 3D로 렌더링합니다.</p>
        <fieldset className="option-fieldset" disabled={isProcessing}>
          <div className="option-grid">
            <label>
              모델
              <select value={model} onChange={(e) => setModel(e.target.value as "Small" | "Base" | "Large")}>
                <option value="Small">Small</option>
                <option value="Base">Base</option>
                <option value="Large">Large</option>
              </select>
            </label>
            <label>
              메시 방식
              <select value={meshMethod} onChange={(e) => setMeshMethod(e.target.value as "poisson" | "bpa")}>
                <option value="poisson">Poisson</option>
                <option value="bpa">BPA</option>
              </select>
            </label>
            <label>
              Voxel Size
              <input
                type="number"
                min={0.005}
                max={0.2}
                step={0.005}
                value={voxelSize}
                onChange={(e) => setVoxelSize(Number(e.target.value))}
              />
            </label>
            <label>
              Depth Trunc
              <input
                type="number"
                min={0.3}
                max={20}
                step={0.1}
                value={depthTrunc}
                onChange={(e) => setDepthTrunc(Number(e.target.value))}
              />
            </label>
          </div>
          <div className="actions">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            <button onClick={() => createJobMutation.mutate()} disabled={isProcessing}>
              {isProcessing ? "처리 중..." : "처리 시작"}
            </button>
          </div>
        </fieldset>
        {isProcessing ? (
          <div className="wait-banner" role="status" aria-live="polite">
            <span className="spinner" />
            <span>
              처리 중입니다. 잠시만 기다려 주세요
              {jobQuery.data?.status ? ` (${jobQuery.data.status})` : ""}…
            </span>
          </div>
        ) : null}
        <div className="toggles">
          <label>
            <input type="checkbox" checked={showVoxels} onChange={(e) => setShowVoxels(e.target.checked)} />
            복셀 표시
          </label>
          <label>
            <input type="checkbox" checked={showMesh} onChange={(e) => setShowMesh(e.target.checked)} />
            메시 표시
          </label>
        </div>
        <div className="status">
          <span>상태: {jobQuery.data?.status ?? "idle"}</span>
          <span>메시지: {jobQuery.data?.message ?? "-"}</span>
        </div>
        {jobQuery.data?.artifacts.depth_color_url ? (
          <div className="preview-area">
            <img src={jobQuery.data.artifacts.depth_color_url} alt="depth preview" className="depth-preview" />
          </div>
        ) : null}
        {jobQuery.data?.status === "done" ? (
          <div className="downloads">
            {jobQuery.data.artifacts.depth_color_url ? <a href={jobQuery.data.artifacts.depth_color_url} target="_blank" rel="noreferrer">Depth PNG</a> : null}
            {jobQuery.data.artifacts.voxels_url ? <a href={jobQuery.data.artifacts.voxels_url} target="_blank" rel="noreferrer">Voxels JSON</a> : null}
            {jobQuery.data.artifacts.mesh_url ? <a href={jobQuery.data.artifacts.mesh_url} target="_blank" rel="noreferrer">Mesh JSON</a> : null}
            {jobQuery.data.artifacts.point_cloud_url ? <a href={jobQuery.data.artifacts.point_cloud_url} target="_blank" rel="noreferrer">Cloud PLY</a> : null}
            {jobQuery.data.artifacts.mesh_obj_url ? <a href={jobQuery.data.artifacts.mesh_obj_url} target="_blank" rel="noreferrer">Mesh OBJ</a> : null}
          </div>
        ) : null}
      </header>

      <section className="viewer-panel">
        {voxels.length > 0 ? (
          <MeshViewer voxels={voxels} voxelSize={voxelSize} mesh={mesh} showVoxels={showVoxels} showMesh={showMesh} />
        ) : (
          <div className="placeholder">처리 완료 후 3D 결과가 표시됩니다.</div>
        )}
      </section>
    </main>
  );
}
