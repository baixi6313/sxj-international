const ci = require('miniprogram-ci');
const privateKeyPath = process.argv[2]; // .key 文件路径，命令行传入
const version = process.argv[3] || '1.0.0';
const desc = process.argv[4] || '事现鉴小程序首版（纯前端展示）';

if (!privateKeyPath) {
  console.error('用法: node upload.js <私钥.key路径> [版本号] [备注]');
  process.exit(1);
}

const appid = 'wx22ec573cb69acc7a';
const projectPath = 'C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27/sxj-mini/weapp';

(async () => {
  const project = new ci.Project({
    appid,
    type: 'miniProgram',
    projectPath,
    privateKeyPath,
    ignores: ['node_modules/**/*', '.git/**/*'],
  });
  const uploadResult = await ci.upload({
    project,
    version,
    desc,
    setting: { es6: true, minify: true },
    onProgressUpdate: console.log,
  });
  console.log('UPLOAD_SUCCESS:', JSON.stringify(uploadResult));
})().catch(err => {
  console.error('UPLOAD_FAILED:', err);
  process.exit(1);
});
