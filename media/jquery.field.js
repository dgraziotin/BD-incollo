/*
 * jQuery Field Plug-in
 *
 * Copyright (c) 2007 Dan G. Switzer, II
 *
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 * Revision: 14
 * Version: 0.9.2
*/
(function($){var defaults={delimiter:",",checkboxRangeKeyBinding:"shiftKey",useArray:false};$.Field={version:"0.9.2",setDefaults:function(options){$.extend(defaults,options)},setProperty:function(prop,value){defaults[prop]=value},getProperty:function(prop){return defaults[prop]}};$.fn.fieldArray=function(v){var t=$type(v);if(t=="undefined")return getValue(this);if(t=="string"||t=="number"){v=v.toString().split(defaults.delimiter);t="array"}if(t=="array")return setValue(this,v);return this};$.fn.getValue=function(){return getValue(this).join(defaults.delimiter)};var getValue=function(jq){var v=[];jq.each(function(lc){var t=getType(this);switch(t){case"checkbox":case"radio":if(this.checked)v.push(this.value);break;case"select":if(this.type=="select-one"){v.push((this.selectedIndex==-1)?"":getOptionVal(this[this.selectedIndex]))}else{for(var i=0;i<this.length;i++){if(this[i].selected){v.push(getOptionVal(this[i]))}}}break;case"text":v.push(this.value);break}});return v};$.fn.setValue=function(v){return setValue(this,((!v&&(v!==0))?[""]:v.toString().split(defaults.delimiter)))};var setValue=function(jq,v){jq.each(function(lc){var t=getType(this),x;switch(t){case"checkbox":case"radio":if(valueExists(v,this.value))this.checked=true;else this.checked=false;break;case"select":var bSelectOne=(this.type=="select-one");var bKeepLooking=true;for(var i=0;i<this.length;i++){x=getOptionVal(this[i]);bSelectItem=valueExists(v,x);if(bSelectItem){this[i].selected=true;if(bSelectOne){bKeepLooking=false;break}}else if(!bSelectOne)this[i].selected=false}if(bSelectOne&&bKeepLooking&&!!this[0]){this[0].selected=true}break;case"text":this.value=v.join(defaults.delimiter);break}});return jq};$.fn.formHash=function(inHash){var bGetHash=(arguments.length==0);var stHash={};this.filter("form").each(function(){var els=this.elements,el,n,stProcessed={},jel;for(var i=0,elsMax=els.length;i<elsMax;i++){el=els[i];n=el.name;if(!n||stProcessed[n])continue;var jel=$(el.tagName.toLowerCase()+"[name='"+n+"']",this);if(bGetHash){stHash[n]=jel[defaults.useArray?"fieldArray":"getValue"]()}else if(typeof inHash[n]!="undefined"){jel[defaults.useArray?"fieldArray":"setValue"](inHash[n])}stProcessed[n]=true}});return(bGetHash)?stHash:this};$.fn.autoAdvance=function(callback){return this.find(":text,:password,textarea").bind("keyup.autoAdvance",function(e){var $field=$(this),iMaxLength=parseInt($field.attr("maxlength"),10);if(isNaN(iMaxLength)||("|9|16|37|38|39|40|".indexOf("|"+e.keyCode+"|")>-1))return true;if($field.getValue().length>=$field.attr("maxlength")){var $next=$field.moveNext().select();if($.isFunction(callback))callback.apply($field,[$next])}})};$.fn.moveNext=function(){return this.moveIndex("next")};$.fn.movePrev=function(){return this.moveIndex("prev")};$.fn.moveIndex=function(i){var aPos=getFieldPosition(this);if(i=="next")i=aPos[0]+1;else if(i=="prev")i=aPos[0]-1;if(i<0)i=aPos[1].length-1;else if(i>=aPos[1].length)i=0;return $(aPos[1][i]).trigger("focus")};$.fn.getTabIndex=function(){return getFieldPosition(this)[0]};var getFieldPosition=function(jq){var $field=jq.filter("input, select, textarea").get(0),aTabIndex=[],aPosIndex=[];if(!$field)return[-1,[]];$.each($field.form.elements,function(i,o){if(o.tagName!="FIELDSET"&&!o.disabled){if(o.tabIndex>0){aTabIndex.push(o)}else{aPosIndex.push(o)}}});aTabIndex.sort(function(a,b){return a.tabIndex-b.tabIndex});aTabIndex=$.merge(aTabIndex,aPosIndex);for(var i=0;i<aTabIndex.length;i++){if(aTabIndex[i]==$field)return[i,aTabIndex]}return[-1,aTabIndex]};$.fn.limitSelection=function(limit,options){var opt=jQuery.extend((limit&&limit.constructor==Object?limit:{limit:limit,onsuccess:function(limit){return true},onfailure:function(limit){alert("You can only select a maximum a of "+limit+" items.");return false}}),options);var self=this;var getCount=function(el){if(el.type=="select-multiple")return $("option:selected",self).length;else if(el.type=="checkbox")return self.filter(":checked").length;return 0};var undoSelect=function(){setValue(self,getValue(self).slice(0,opt.limit));return opt.onfailure.apply(self,[opt.limit])};return this.bind((!!self[0]&&self[0].type=="select-multiple")?"change.limitSelection":"click.limitSelection",function(){if(getCount(this)>opt.limit){return(this.type=="select-multiple")?undoSelect():opt.onfailure.apply(self,[opt.limit])}opt.onsuccess.apply(self,[opt.limit]);return true})};$.fn.createCheckboxRange=function(callback){var opt=jQuery.extend((callback&&callback.constructor==Object?callback:{bind:defaults.checkboxRangeKeyBinding,onclick:callback}),callback);var iLastSelection=0,self=this,bCallback=$.isFunction(opt.onclick);if(bCallback)this.each(function(){opt.onclick.apply(this,[$(this).is(":checked")])});return this.each(function(){if(this.type!="checkbox")return false;var el=this;var updateLastCheckbox=function(e){iLastSelection=self.index(e.target)};var checkboxClicked=function(e){var bSetChecked=this.checked,current=self.index(e.target),low=Math.min(iLastSelection,current),high=Math.max(iLastSelection+1,current);if(bCallback)$(this).each(function(){opt.onclick.apply(this,[bSetChecked])});if(!e[opt.bind])return;for(var i=low;i<high;i++){var item=self.eq(i).attr("checked",bSetChecked?"checked":"");if(bCallback)opt.onclick.apply(item[0],[bSetChecked])}return true};$(this).unbind("click.createCheckboxRange").bind("click.createCheckboxRange",checkboxClicked).bind("click.createCheckboxRange",updateLastCheckbox);return true})};var getType=function(el){var t=el.type;switch(t){case"select":case"select-one":case"select-multiple":t="select";break;case"text":case"hidden":case"textarea":case"password":case"button":case"submit":case"submit":t="text";break;case"checkbox":case"radio":t=t;break}return t};var getOptionVal=function(el){return jQuery.browser.msie&&!(el.attributes['value'].specified)?el.text:el.value};var valueExists=function(a,v){return($.inArray(v,a)>-1)};var $type=function(o){var t=(typeof o).toLowerCase();if(t=="object"){if(o instanceof Array)t="array";else if(o instanceof Date)t="date"}return t};var $isType=function(o,v){return($type(o)==String(v).toLowerCase())}})(jQuery);