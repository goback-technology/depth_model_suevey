module.exports = {
  apps: [
    {
      name: "dap3d-backend",
      cwd: "/home/agent01/works/depth_model_suevey",
      script: "uv",
      args: [
        "run",
        "uvicorn",
        "--app-dir",
        "web_demo/backend",
        "app.main:app",
        "--port",
        "21031",
      ],
      interpreter: "none",
      autorestart: true,
      max_restarts: 10,
      restart_delay: 2000,
      time: true,
      env: {
        PYTHONUNBUFFERED: "1",
      },
    },
  ],
};
