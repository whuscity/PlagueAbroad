## 海外疫情信息集成平台后台管理

注：导入csv时需要header内容，同时header内容需要和数据库字段保持一致

数据源表

<table>
   <tr>
      <td>字段名</td>
      <td>类型</td>
      <td>描述</td>
   </tr>
   <tr>
      <td>id</td>
      <td>int</td>
      <td>主键</td>
   </tr>
   <tr>
      <td>name</td>
      <td>varchar</td>
      <td>数据来源名称</td>
   </tr>
   <tr>
      <td>link</td>
      <td>varchar</td>
      <td>数据来源链接</td>
   </tr>
   <tr>
      <td>description</td>
      <td>varchar</td>
      <td>数据来源描述</td>
   </tr>
</table>

文章表

<table>
   <tr>
      <td>字段名</td>
      <td>类型</td>
      <td>描述</td>
   </tr>
   <tr>
      <td>id</td>
      <td>int</td>
      <td>主键</td>
   </tr>
   <tr>
      <td>direct_source_id</td>
      <td>int</td>
      <td>文章直接来源(外键)</td>
   </tr>
   <tr>
      <td>original_source_id</td>
      <td>int</td>
      <td>文章初始来源(外键)</td>
   </tr>
   <tr>
      <td>original_source_name</td>
      <td>varchar</td>
      <td>文章初始来源名称</td>
   </tr>
   <tr>
      <td>nick_name</td>
      <td>varchar</td>
      <td>只有来源自社交媒体才有</td>
   </tr>
   <tr>
      <td>url</td>
      <td>varchar</td>
      <td>文章来源链接</td>
   </tr>
   <tr>
      <td>title</td>
      <td>varchar</td>
      <td>文章标题</td>
   </tr>
   <tr>
      <td>abstract</td>
      <td>varchar</td>
      <td>文章摘要(不一定有)_</td>
   </tr>
   <tr>
      <td>text</td>
      <td>text</td>
      <td>文章内容</td>
   </tr>
   <tr>
      <td>publish_time</td>
      <td>datetime</td>
      <td>发布时间</td>
   </tr>
   <tr>
      <td>access_time</td>
      <td>datetime</td>
      <td>收集时间</td>
   </tr>
   <tr>
      <td>location</td>
      <td>varchar</td>
      <td>国家地区</td>
   </tr>
   <tr>
      <td>type</td>
      <td>varchar</td>
      <td>文章类型</td>
   </tr>
</table>

字段顺序在csv中无须一致