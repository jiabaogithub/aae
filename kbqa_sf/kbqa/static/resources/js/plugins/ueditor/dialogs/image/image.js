!function(){var o,r;function a(t){if(t){var e,i,a=$G("tabhead").children;for(e=0;e<a.length;e++)(i=a[e].getAttribute("data-content-id"))==t?(domUtils.addClass(a[e],"focus"),domUtils.addClass($G(i),"focus")):(domUtils.removeClasses(a[e],"focus"),domUtils.removeClasses($G(i),"focus"));switch(t){case"remote":o=o||new s;break;case"upload":n(editor.getOpt("imageInsertAlign")),r=r||new l("queueList")}}}function n(t){t=t||"none";var e=$G("alignIcon").children;for(i=0;i<e.length;i++)e[i].getAttribute("data-align")==t?(domUtils.addClass(e[i],"focus"),$G("align").value=e[i].getAttribute("data-align")):domUtils.removeClasses(e[i],"focus")}function s(t){this.container=utils.isString(t)?document.getElementById(t):t,this.init()}function l(t){this.$wrap=t.constructor==String?$("#"+t):$(t),this.init()}window.onload=function(){!function(){for(var t=$G("tabhead").children,e=0;e<t.length;e++)domUtils.on(t[e],"click",function(t){var e=t.target||t.srcElement;a(e.getAttribute("data-content-id"))});var i=editor.selection.getRange().getClosedNode();i&&i.tagName&&"img"==i.tagName.toLowerCase()?a("remote"):a("upload")}(),domUtils.on($G("alignIcon"),"click",function(t){var e=t.target||t.srcElement;e.className&&-1!=e.className.indexOf("-align")&&n(e.getAttribute("data-align"))}),dialog.onok=function(){for(var t,e=[],i=$G("tabhead").children,a=0;a<i.length;a++)if(domUtils.hasClass(i[a],"focus")){t=i[a].getAttribute("data-content-id");break}switch(t){case"remote":e=o.getInsertList();break;case"upload":e=r.getInsertList()}e&&0<e.length?editor.execCommand("insertimage",e):$.notifyError("请上传文件")}},s.prototype={init:function(){this.initContainer(),this.initEvents()},initContainer:function(){this.dom={url:$G("url"),width:$G("width"),height:$G("height"),border:$G("border"),vhSpace:$G("vhSpace"),title:$G("title"),align:$G("align")};var t=editor.selection.getRange().getClosedNode();t&&this.setImage(t)},initEvents:function(){var e=this,i=$G("lock");function a(){e.setPreview()}domUtils.on($G("url"),"keyup",a),domUtils.on($G("border"),"keyup",a),domUtils.on($G("title"),"keyup",a),domUtils.on($G("width"),"keyup",function(){if(i.checked){var t=i.getAttribute("data-proportion");$G("height").value=Math.round(this.value/t)}else e.updateLocker();a()}),domUtils.on($G("height"),"keyup",function(){if(i.checked){var t=i.getAttribute("data-proportion");$G("width").value=Math.round(this.value*t)}else e.updateLocker();a()}),domUtils.on($G("lock"),"change",function(){var t=parseInt($G("width").value)/parseInt($G("height").value);i.setAttribute("data-proportion",t)})},updateLocker:function(){var t=$G("width").value,e=$G("height").value,i=$G("lock");t&&e&&t==parseInt(t)&&e==parseInt(e)?(i.disabled=!1,i.title=""):(i.checked=!1,i.disabled="disabled",i.title=lang.remoteLockError)},setImage:function(t){if(t.tagName&&("img"==t.tagName.toLowerCase()||t.getAttribute("src"))&&t.src){var e=t.getAttribute("word_img"),i=e?e.replace("&amp;","&"):t.getAttribute("_src")||t.getAttribute("src",2).replace("&amp;","&"),a=editor.queryCommandValue("imageFloat");i!==$G("url").value&&($G("url").value=i),i&&($G("width").value=t.width||"",$G("height").value=t.height||"",$G("border").value=t.getAttribute("border")||"0",$G("vhSpace").value=t.getAttribute("vspace")||"0",$G("title").value=t.title||t.alt||"",n(a),this.setPreview(),this.updateLocker())}},getData:function(){var t={};for(var e in this.dom)t[e]=this.dom[e].value;return t},setPreview:function(){var t,e,i=$G("url").value,a=$G("width").value,o=$G("height").value,r=$G("border").value,n=$G("title").value,s=$G("preview");t=(t=a&&o?Math.min(a,s.offsetWidth):s.offsetWidth)+2*r>s.offsetWidth?t:s.offsetWidth-2*r,e=a&&o?t*o/a:"",i&&(s.innerHTML='<img src="'+i+'" width="'+t+'" height="'+e+'" border="'+r+'px solid #000" title="'+n+'" />')},getInsertList:function(){var t=this.getData();return t.url?[{src:t.url,_src:t.url,width:t.width||"",height:t.height||"",border:t.border||"",floatStyle:t.align||"",vspace:t.vhSpace||"",alt:t.title||"",style:"width:"+t.width+"px;height:"+t.height+"px;"}]:[]}},l.prototype={init:function(){this.imageList=[],this.initUploader()},initUploader:function(){$("#insert-img-uploader").fileinput({theme:"fa",language:"zh",uploadUrl:"/api/system/file/batch-upload",layoutTemplates:{actions:'<div class="file-actions"><div class="file-footer-buttons">{download} {delete} {zoom} {other}</div></div>{drag}<div class="clearfix"></div>'},browseClass:"btn btn-primary btn-raised btn-sm float-right mr-2",showClose:!1,showCaption:!1,removeLabel:"清空",removeClass:"btn btn-danger btn-raised btn-sm float-right",uploadClass:"btn btn-success btn-raised btn-sm float-right mr-2",allowedFileExtensions:["jpg","jpeg","gif","png"]}),$("#insert-img-uploader").on("fileuploaded",this,function(t,e,i,a){var o=t.data;e.response&&o.imageList.push(e.response)})},getInsertList:function(){for(var t=[],e=0;e<this.imageList.length;e++)t.push({src:"/api/system/file/showimage/"+this.imageList[e],width:150,height:150});return t}}}();