# macOS

macOS 可原生运行 Web、SDK 和 tmux/PTY CLI 模式。系统使用 seatbelt 沙箱，不需要安装 bubblewrap。

```bash
brew install tmux gh
gh auth login
gh auth setup-git
uv tool install --force --python 3.12 "git+https://github.com/professoryu06/omnigent-zh-cn.git"
omnigent-zh platform-info
omnigent-zh setup
```

仍需自行安装 Node.js 22 LTS+。首次从私有 Git 源安装会构建中文 Web UI。GitHub Actions 的 macOS 工作流只验证安装、构建和服务健康；模型登录与真实 CLI 调用必须在使用者自己的设备上完成。
