# 创建文件夹
rm -rf ~/git_ha_sidebar
mkdir ~/git_ha_sidebar
cd ~/git_ha_sidebar
# 拉取新文件
git init
git remote add -f origin https://github.com/shaonianzhentan/ha_sidebar
git config core.sparsecheckout true
echo "custom_components/ha_sidebar" >> .git/info/sparse-checkout
cat .git/info/sparse-checkout
git pull origin master
# 更新文件
cp -rf ~/git_ha_sidebar/custom_components/ha_sidebar '$source_path'