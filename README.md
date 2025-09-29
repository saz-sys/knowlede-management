# Engineering Knowledge Sharing Platform

エンジニアリング知識共有プラットフォーム - 安全で信頼性の高い開発環境を提供します。

## セキュリティ機能

このプロジェクトは[Aikido Safe Chain](https://github.com/AikidoSec/safe-chain)を統合しており、マルウェアから開発環境を保護します。

### Aikido Safe Chainについて

- **マルウェア検出**: npm、yarn、pnpmパッケージのマルウェアを自動検出
- **サプライチェーン保護**: 依存関係の悪意のあるパッケージをブロック
- **CI/CD統合**: Dockerビルド時にも自動的にチェック実行
- **package-lock.json使用**: 依存関係の自動更新を防止し、確定的なビルドを保証

### セキュリティガイドライン

⚠️ **重要**: このプロジェクトでは`npm ci`を使用して依存関係をインストールします。

- ✅ **推奨**: `npm ci` - package-lock.jsonを厳密に参照
- ❌ **非推奨**: `npm install` - 依存関係が自動更新される危険性（プロジェクト依存関係の場合）
- ✅ **例外**: `npm install -g` - グローバルパッケージのインストール時のみ使用
- 🔒 **セキュリティ**: 新しいパッケージを追加する際は、必ず`package-lock.json`を更新

## 開発環境セットアップ

### 前提条件

- Node.js 18以上
- Docker（オプション）

### ローカル開発環境のセットアップ

1. **リポジトリのクローン**
```bash
git clone <repository-url>
cd github-knowlede-management
```

3. **依存関係のインストール**
```bash
# 安全なインストール（マルウェアチェック付き、package-lock.json使用）
npm run install-safe

# または通常のインストール（package-lock.json使用）
npm ci
```

4. **開発サーバーの起動**
```bash
npm run dev
```

### Docker環境でのセットアップ

```bash
# Dockerイメージのビルド（自動的にマルウェアチェック実行）
docker build -t knowledge-management .

# コンテナの実行
docker run -p 3000:3000 knowledge-management

# または docker-compose を使用
docker-compose up web
```

### デバッグ方法

```bash
# デバッグ用コンテナを起動
docker-compose up debug

# 別のターミナルでコンテナにログイン
docker exec -it eks-debug bash

# Safe Chainの動作確認
safe-chain --version
npm ci --verbose
```

## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.wwwave.info/s-anzai/knowledge-management.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://gitlab.wwwave.info/s-anzai/knowledge-management/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
