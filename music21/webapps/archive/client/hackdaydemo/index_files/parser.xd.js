/*
	Copyright (c) 2004-2009, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


window[(typeof (djConfig)!="undefined"&&djConfig.scopeMap&&djConfig.scopeMap[0][1])||"dojo"]._xdResourceLoaded(function(_1,_2,_3){return {depends:[["provide","dojo.parser"],["require","dojo.date.stamp"]],defineResource:function(_4,_5,_6){if(!_4._hasResource["dojo.parser"]){_4._hasResource["dojo.parser"]=true;_4.provide("dojo.parser");_4.require("dojo.date.stamp");_4.parser=new function(){var d=_4;this._attrName=d._scopeName+"Type";this._query="["+this._attrName+"]";function _7(_8){if(d.isString(_8)){return "string";}if(typeof _8=="number"){return "number";}if(typeof _8=="boolean"){return "boolean";}if(d.isFunction(_8)){return "function";}if(d.isArray(_8)){return "array";}if(_8 instanceof Date){return "date";}if(_8 instanceof d._Url){return "url";}return "object";};function _9(_a,_b){switch(_b){case "string":return _a;case "number":return _a.length?Number(_a):NaN;case "boolean":return typeof _a=="boolean"?_a:!(_a.toLowerCase()=="false");case "function":if(d.isFunction(_a)){_a=_a.toString();_a=d.trim(_a.substring(_a.indexOf("{")+1,_a.length-1));}try{if(_a.search(/[^\w\.]+/i)!=-1){return new Function(_a);}else{return d.getObject(_a,false);}}catch(e){return new Function();}case "array":return _a?_a.split(/\s*,\s*/):[];case "date":switch(_a){case "":return new Date("");case "now":return new Date();default:return d.date.stamp.fromISOString(_a);}case "url":return d.baseUrl+_a;default:return d.fromJson(_a);}};var _c={};_4.connect(_4,"extend",function(){_c={};});function _d(_e){if(!_c[_e]){var _f=d.getObject(_e);if(!d.isFunction(_f)){throw new Error("Could not load class '"+_e+"'. Did you spell the name correctly and use a full path, like 'dijit.form.Button'?");}var _10=_f.prototype;var _11={},_12={};for(var _13 in _10){if(_13.charAt(0)=="_"){continue;}if(_13 in _12){continue;}var _14=_10[_13];_11[_13]=_7(_14);}_c[_e]={cls:_f,params:_11};}return _c[_e];};this._functionFromScript=function(_15){var _16="";var _17="";var _18=_15.getAttribute("args");if(_18){d.forEach(_18.split(/\s*,\s*/),function(_19,idx){_16+="var "+_19+" = arguments["+idx+"]; ";});}var _1a=_15.getAttribute("with");if(_1a&&_1a.length){d.forEach(_1a.split(/\s*,\s*/),function(_1b){_16+="with("+_1b+"){";_17+="}";});}return new Function(_16+_15.innerHTML+_17);};this.instantiate=function(_1c,_1d,_1e){var _1f=[],dp=_4.parser;_1d=_1d||{};_1e=_1e||{};d.forEach(_1c,function(_20){if(!_20){return;}var _21=dp._attrName in _1d?_1d[dp._attrName]:_20.getAttribute(dp._attrName);if(!_21||!_21.length){return;}var _22=_d(_21),_23=_22.cls,ps=_23._noScript||_23.prototype._noScript;var _24={},_25=_20.attributes;for(var _26 in _22.params){var _27=_26 in _1d?{value:_1d[_26],specified:true}:_25.getNamedItem(_26);if(!_27||(!_27.specified&&(!_4.isIE||_26.toLowerCase()!="value"))){continue;}var _28=_27.value;switch(_26){case "class":_28="className" in _1d?_1d.className:_20.className;break;case "style":_28="style" in _1d?_1d.style:(_20.style&&_20.style.cssText);}var _29=_22.params[_26];if(typeof _28=="string"){_24[_26]=_9(_28,_29);}else{_24[_26]=_28;}}if(!ps){var _2a=[],_2b=[];d.query("> script[type^='dojo/']",_20).orphan().forEach(function(_2c){var _2d=_2c.getAttribute("event"),_21=_2c.getAttribute("type"),nf=d.parser._functionFromScript(_2c);if(_2d){if(_21=="dojo/connect"){_2a.push({event:_2d,func:nf});}else{_24[_2d]=nf;}}else{_2b.push(nf);}});}var _2e=_23.markupFactory||_23.prototype&&_23.prototype.markupFactory;var _2f=_2e?_2e(_24,_20,_23):new _23(_24,_20);_1f.push(_2f);var _30=_20.getAttribute("jsId");if(_30){d.setObject(_30,_2f);}if(!ps){d.forEach(_2a,function(_31){d.connect(_2f,_31.event,null,_31.func);});d.forEach(_2b,function(_32){_32.call(_2f);});}});if(!_1d._started){d.forEach(_1f,function(_33){if(!_1e.noStart&&_33&&_33.startup&&!_33._started&&(!_33.getParent||!_33.getParent())){_33.startup();}});}return _1f;};this.parse=function(_34,_35){var _36;if(!_35&&_34&&_34.rootNode){_35=_34;_36=_35.rootNode;}else{_36=_34;}var _37=d.query(this._query,_36);return this.instantiate(_37,null,_35);};}();(function(){var _38=function(){if(_4.config.parseOnLoad){_4.parser.parse();}};if(_4.exists("dijit.wai.onload")&&(_5.wai.onload===_4._loaders[0])){_4._loaders.splice(1,0,_38);}else{_4._loaders.unshift(_38);}})();}}};});