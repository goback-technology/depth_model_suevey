export type JobStatus = "queued" | "running" | "done" | "failed";

export type Job = {
  job_id: string;
  status: JobStatus;
  message: string;
  artifacts: {
    depth_color_url: string | null;
    voxels_url: string | null;
    point_cloud_url: string | null;
    mesh_url: string | null;
    mesh_obj_url: string | null;
  };
};

export type CreateJobInput = {
  image: File;
  model: "Small" | "Base" | "Large";
  meshMethod: "poisson" | "bpa";
  voxelSize: number;
  depthTrunc: number;
};

export async function createJob(input: CreateJobInput): Promise<{ job_id: string; status: JobStatus }> {
  const formData = new FormData();
  formData.append("image", input.image);
  formData.append("model", input.model);
  formData.append("mesh_method", input.meshMethod);
  formData.append("voxel_size", String(input.voxelSize));
  formData.append("depth_trunc", String(input.depthTrunc));

  const res = await fetch("/api/v1/jobs", {
    method: "POST",
    body: formData
  });
  if (!res.ok) {
    throw new Error("잡 생성 실패");
  }
  return res.json();
}

export async function getJob(jobId: string): Promise<Job> {
  const res = await fetch(`/api/v1/jobs/${jobId}`);
  if (!res.ok) {
    throw new Error("잡 조회 실패");
  }
  return res.json();
}

export async function getVoxels(url: string): Promise<{ points: [number, number, number][]; voxel_size: number }> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error("복셀 데이터 로드 실패");
  }
  return res.json();
}

export async function getMesh(url: string): Promise<{ vertices: [number, number, number][]; faces: [number, number, number][] }> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error("메시 데이터 로드 실패");
  }
  return res.json();
}

export async function getBackendVersion(): Promise<string> {
  const res = await fetch("/api/v1/version");
  if (!res.ok) {
    throw new Error("백엔드 버전 조회 실패");
  }
  const data = (await res.json()) as { version: string };
  return data.version;
}
