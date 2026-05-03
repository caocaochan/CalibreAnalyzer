"""
HSK 3.0 character data by level.
Source: Official 《国际中文教育中文水平等级标准》
Characters are non-cumulative (each level lists only NEW characters).
"""

import base64
import json
import zlib

# Maps HSK level label -> set of characters for that level
HSK_LEVELS = {
    "1": set(
        "一七三上下不东两个中么九也习书买了事二五些亮人什今他以们件休会住作你便候做儿元先八公六关兴再写冷几出分到前包医十千午半卖去友口只叫可号司吃同名后吗吧听呢和哥哪唱商喂喜喝四回国在坐块士外多大天太女奶她好妈妹姐子字学孩它宜客家对小少岁工市师常年床开弟影很得忙怎息您想我房手打找文新日早时明星昨是晚月有朋服期本机条来杯果校样桌椅欢歌正气水汉没漂火点热爱爸牛狗猫玩现班生电男病白百的看真睡知租穿第米系给老能脑苹茶菜蛋衣西要见视觉认识话语说请读课谁谢贵起超车边还这道那都里钟钱问间院雨雪零非面题飞饭高鸡"
    ),
    "2": set(
        "万丈为乐交介从但位体准别动右告周咖啊啡因地场坏备夫头妻始姓完室就左己已希帮店往忘快思情意慢懂所拿教旁旅晴最望楼次步每比泳洗游然爷球画留疼眼着睛票离站笑笔等篮累红绍经绿网考肉自舒舞色花药虽表裤让记诉词试走足跑跟路跳踢身过运近进远送酒铁错长门阴颜馆鱼鸟黑"
    ),
    "3": set(
        "且世业丢主久乎于伞信借假健像全共其典养冒冬冰决净凉凌刚初刮刷刻力办加务助努勺化北区单南卡卫历参又双发叔受变句史合向员咱响哭啤嘴园图坚城境声处复夏奇如姨婚季安定实害容宾封尝层居屋展山差带干平应康张当心必怕急怪总惯感愿戏成或才扫把护报担拍择持挺换据接提搬收放故数料斤方旧易春更末朵李束板极查树根梯检楚概段毛求汽沙河泉法注活海清渴满演澡激灯炼烧照熊爬片牙物特环理瓜瓶甜用界瘦盘目直相短矮矿码碗礼秋种空突答筷简算箱糕糖级纸练终结绩羊羽者而耳聊聪育胖脏脚脸腿般船节草蓝蕉行街衫衬被裙角解言议讲该调赛越趣轻较辆迎迟适选遇遍邮邻重铅银锻闻阳阿附除难需静鞋音页须顾风饮饱饺饿香马骑鲜黄"
    ),
    "4": set(
        "与专严丰丽举之乒乓乘乡乱争云互亚产京亲仅仍仔付价任份众优伙伤估低何使例供保俩修倍倒值停偶傅傲允兄光克免入具内农况减刀切划列则判利剧剩功励勇匙博印危即却厂厅厉压厌厕厚原厨及反取另台叶各否吸吹味呼命咳咸品售喊嗯嗽困围土圾址垃基堂堵塑填增夜够失奋奖套姑娘存孙寄密富寒察导将尊尔尤尽巧巴巾帅帽幅并幸幽广庆序底度座庭建弃弄式引弹强彩待律微忆志忽怀态性恐恼悉悔惊惜愉慕懒戚戴户扔扬扰批技折抬抱拉拒招拾挂指按授掉排推摄播操擦支改效敢散敲整断族无既晨普景暂暑暖术杂材村松林染柿标格案桥桶梦棒森棵植歉止此死母毕氏民永汁汗江污汤油泼洋洲流济浪消深温漫烟烤烦熟父牌猜琴甚由申疑痛登皮盐盒省研破础硕确示社祝禁福秀科秒积程稍究窗竞竟章童符笨签管篇籍粗精紧约纪线组细绝继续缺美羞羡翻耐职联聘聚肚肤肯背胳脱脾膊膏至航艺苦获萄落著葡虎虑血袋袜装观规警计订讨许论证评译诚详误谅谈谊象貌负责败账货质购费贺资赚赢赶趟距躺转输辛辣达连迷递通逛速邀郊部酸醒释量金针钢钥键镜闹阅队际降险陪随青项顺顿预频食餐饼馒首骄验麻默鼓鼻龄"
    ),
    "5": set(
        "丑临义乏乙亏享亿代令仿企伍伟传伴伸似余佛佳依促俗倡傍催傻充兔册军冠冲冻凭创删制刺剪副劝劳势勤匹升华协占卧卷厘厢厦县叉古召吨含吵呀咨咬哈哎哦哲唉唯善喻嘉器团固圆均型域培堆墙夕奈妇姥姿威娱婆媒守宝宠宣宽宿寓寻尺尾局届屏属巨币布席幕幼库府延弯弱录形彻彼征忍念怨恋恢恭悄悠惠慎慧慰憾战扇扣执扩扮扶承抓投抢押抽拆拖拥拨括拼挑挡挣挤挥捐损捡掌控措描插握搜搞摇摔摘摸撞擅政敌敏救敬斗斜施旦昆映显晒智暗暴曲曾替朝木未权构析架某柜桃档梨模橘橙橡欠欣欧款武殊汇池沉沟治沿泛泪洒洞派浅浆浇测浏浓润涨淡渐湖湿源滑滚漏漠灰灵炒炸烈煮熬燃版状犹狂独猪献猴率玉玫玻珍瑰璃甲番疗疯疾盆益盖盾眠矛石硬碌碎碰神祸私秘称移税稳穷窄立竹筑类粮糊糟素索紫繁纷织绕络统绪维综缓缩罚置群翅肃肌肖肥胁胃胆胜胡腐腰膀臭致舍良艰范茄荐荣营蔬薄藏虚虫蛇蝴蝶衡补裁裹览触训设访诊诗询谨豆豫贝贡贴赏赔赞赠趋践蹈躲软载辑辞迅返违述迹追退逐途造逻遗遵避郎配醉采铃销锁锅闭闲防阵阶阻陆陌限隔集雾震靠革领颗饰驶驾骂骗魅鸭鼠齐齿龙"
    ),
    "6": set(
        "丧串乌予井亡仓仗仪仰佩侄侧俱倾偷偿储兰兵兼凡击刊券刹剑割劣劲勉匀匆叙吉吊吐吓吞启呆呈哇啦喷嗓嘛嘲嘿噪圈坛坡垂埋塔塞壁壤壮壶央夸夹夺奉奏奔妆妙妨委姻娃娶婴媳嫁嫌孕孤宅宏官审宫宴宵寂寞寸寿射尖尘尚尬尴屈履岗岛岸峰崇崭州巩帆帝幻庄庞廊异弥归径徒循德忧怒怜恨恰恶患悲惑惧惩愁愤戒截扎扑托扭抄抑抗抛披抵拐拔拜拟拦挖挫捉捕捧捷掏探援搭携摆摩撑撒撤攻旋旗旬旱昂晕晰晾朗朴杀杰枕枝枪枯柔柴栋栏株核梁梅械棉棋棍棕椎椒榜横欲欺歇歪残殖毒毫氛氧汰沃泡泥洁洪浮浴涉涌液涵淋淘混淹添渠渡港滴漱潜潮灭灾炎烂烫焦煤燥爆牢牵犯狠狮狼王珠瓷甥田畅略疫疲症痒痕皇监盛盲盼眉睁督瞧瞬矩砍砖碍碳祖祥秩稻稼稿竖端笼筒策筛筹箭粉粒粘粥粽纠纯纳绒绘编罐罕罪耗耽肝肠股肩肪肺肿胞胶胸脂脆脖腔臂臣舅舌艘艳英菊菌蓄薪薯虹蚁蚂蜂蜜融衰袖裕覆誉讯讶诞诸诺谐谓谦豪财贫贯贷贸赋赖趁跃跌跪踏踩踪蹲轨轮辅辈迈迫逃透逗逼遥遭酱酷醋野鉴钓钻铜铺链镇闪闯阔陷隐障雄雷露顶顽颈颖额飘饥馈骤骨鲨麦龟"
    ),
    "7-9": set(
        "丁丐丘丙丛丝丫丸丹乃乖乞乳亦亩亭仁仆仇仙仲伏伐伦伪伯伺佑佣侃侈侍侠侣侥侦侨侮侵俊俏俘俭俯倔倘倚倦债偏僚僧僵僻兀兆兑党兜兢兹兽冗冤冶凄凋凑凝凤凯凰凳凶凸凹函凿刁刑刨剂剃削剔剖剥劈劫勃勋勒勘募勾勿匠匪匿卉卑卓卜卤卦卵卸厄叛叠叨叭叮叹叼吁吏君吝吟吩吭吻吼呐呕呛呜呵呻咀咐咕咙咧咽哀哄哆哑哗哨哺哼哽唆唇唐唠唤唬唾啃啬啰啸喇喉喘喧嗅嗜嗦嘀嘈嘱噩嚏嚣嚷嚼囊囚囱圣坊坎坑坝坟坠坦坪坷垄垒垦垫垮堕堡堤堪塌塘墅墓墟墨壳夯夷契奚奠奢奥奴奸妄妒妖妥姆姜娇婉婪婿媚媲嫂嫉嫩嬉孔孝孪孵宁宇宗宙宪宰寐寝寡寥寨寺尸尿屁屉屎屑屠屡屹屿岂岔岖岩岭岳峙峡峭峻崎崖崛崩嵌巅川巡巢巷帐帕帖帘帚帜帷幄幢庇庙废庸廉廓廷弈弊弓弘弛弦彬彰役徊徐徘徙御徽忌忠怂怖怠怡怯恍恒恕恤恩恳恿悟悦悬悴悼惋惕惦惨惫惬惭惮惰惹愈愚愣愧慈慌慑慨慷憋憔憧憨憬懈戈戳扁扒扛扯扳抉抒抖抚抠抡抨抹拄拇拌拎拓拘拙拢拣拧拯拱拳拴拽挎挚挟挠挨挪振挽捂捅捆捍捎捏捞捣捶掀掐掘掠掩掰掷掺揉揍揠揣揪揭揽搀搁搂搅搏搓摊摧撇撕撬撰撵撼擎攀攒攘敛敞敦敷斑斟斥斧斩旨旭旷旺昌昏昔昧昼晃晋晓晤晶暄暧暨暮曙曝曰朦朱朽杆杖杜杠杨枉枚枢枣柄柏柬柱柳栖栽桂框桑桨桩梢梭梳棘棚棱棺椭椰楷榨槐槛槽橱檐歧歹歼殃殴殷殿毁毅毙毯氓汛汪汲汹沏沐沛沧沫沮沸沼沾泄泊泌泞波泣泰泻泽津洽浊浑浩浸涂涕涛涝涡涤涩涮涯淀淆淌淤淳渊渔渗渣渺湃湛湾溃溅溉溜溢溪溯溶溺滋滔滞滤滥滨滩漆漾潇潦潭澄澈澎澜濒瀑瀚灌灶灸灼灿炉炊炖炫炬炭炮烁烘烛烹焕焙焚焰煌煎煲煽熄熏熙熨燕爪爹爽牡牧牲牺犀犬狈狐狡狭狱狸猎猖猛猩猾玄琐琢瑕瑞璀璨瓣瓦甘甩甸畏畔畜畴畸疆疏疙疤疵痪痰痴痹瘟瘤瘩瘫瘸瘾癌皂皆皱盈盏盗盟盯盹眨眯眶眺睐睦睬睹瞄瞅瞎瞒瞩瞪瞻矗矢矣矫砌砸碑碟碧磁磅磊磋磕磨礁祀祈祭祷禅禽禾秃秉秤秧秽稀稚稠稽穴窃窍窑窒窘窜窝窟窥窿竣竭竿笛筋筐筝篷簇簸籽粕粪粹糙紊絮纤纬纱纲纵纹纺纽绅绊绎绑绞绣绯绰绳绵绷绸绽缀缅缆缉缔缕缘缚缝缠缤缴缸罗罢罩署翁翔翘翠翼耀耍耕耘耸耻耿聆聋肆肇肢肴肾胀胎胚胧脉脊腆腊腕腥腹腻腼腾膛膜膝膨膳臀舆舔舟舰舱舵舶艇艾芒芝芬芭芯芳芽苍苏苗苛苟若茁茂茉茎茫荆荒荡荤荧荫荷莅莉莫莲莹莽菇菩萌萍萎萝萧萨董葬葱蒂蒙蒜蒸蓬蔑蔓蔚蔼蔽蕴蕾藐藤藻蘑蘸虏虐虔虾蚀蚊蛀蛙蛮蜡蝇螃螺蟹蠢衅衍衔衷袍袭袱裂裔裳裸褒觅誓譬讥讳讹讼讽诀诈诠诡诧诫诬诱诵诽谋谍谎谜谣谤谬谱谴谷豁豚豹贞贤贩贪贬贮贱贼贾贿赁赂赃赌赎赐赘赡赤赫赴趴跤跨跷踊踹蹊蹋蹦蹬蹭躁躬躯轰轴轿辉辐辕辖辗辙辜辟辨辩辫辰辱辽迁迄迪迭迸逆逊逝逞逢逮逸逾遏遛遣遮邃邪郁郑鄙酌酗酝酣酥酪酬酵酿醇钉钙钝钞钦钧钩钮铭铲铸锄锈锋锐锡锤锦锲镶闷闸闺阀阁阂阎阐阱陈陋陡陨陵陶隆隘隙隧隶雀雁雅雇雌雕雹霉霍霜霞霸靴靶鞠鞭韧韵顷颁颂颇颊颓颠颤飙饪饲饵饶馁馅馋馨驭驮驯驰驱驳驻骇骏骚骼髓髦鬼魁魂魄魔鲁鲤鲸鳄鸣鸦鸽鹅鹏鹤鹰鹿麟黎黏鼎"
    ),
}

# Ordered level labels for display
HSK_LEVEL_ORDER = ["1", "2", "3", "4", "5", "6", "7-9"]


def _load_char_level_map():
    mapping = {}
    for level in HSK_LEVEL_ORDER:
        for char in HSK_LEVELS[level]:
            mapping[char] = level
    return mapping


HSK_CHAR_TO_LEVEL = _load_char_level_map()


def hsk_coverage(unique_chars):
    """
    Given a set/list of unique characters from a book, return a dict mapping
    each HSK level to the percentage of the book's unique characters it covers.
    Also returns cumulative coverage and characters not in any HSK level.
    """
    unique = set(unique_chars)
    total = len(unique)
    if total == 0:
        empty_levels = {lvl: {"count": 0, "pct": 0.0, "chars": set()} for lvl in HSK_LEVEL_ORDER}
        empty_cum = {lvl: {"count": 0, "pct": 0.0} for lvl in HSK_LEVEL_ORDER}
        return {
            "per_level": empty_levels,
            "cumulative": empty_cum,
            "not_in_hsk": set(),
            "not_in_hsk_count": 0,
            "not_in_hsk_pct": 0.0
        }

    per_level = {}
    cumulative = {}
    covered_so_far = set()

    for lvl in HSK_LEVEL_ORDER:
        chars_in_level = unique & HSK_LEVELS[lvl]
        per_level[lvl] = {
            "count": len(chars_in_level),
            "pct": len(chars_in_level) / total * 100,
            "chars": chars_in_level,
        }
        covered_so_far |= chars_in_level
        cumulative[lvl] = {
            "count": len(covered_so_far),
            "pct": len(covered_so_far) / total * 100,
        }

    not_in_hsk = unique - covered_so_far
    return {
        "per_level": per_level,
        "cumulative": cumulative,
        "not_in_hsk": not_in_hsk,
        "not_in_hsk_count": len(not_in_hsk),
        "not_in_hsk_pct": len(not_in_hsk) / total * 100,
    }


HSK_WORD_LEVEL_ORDER = ["1", "2", "3", "4", "5", "6", "7-9"]

_HSK_WORD_DATA_B85 = (
    "c-l<8NpdpJ@-4WRJO0<;-s-GsD`js|W^V&Es7Xy|MBhs^LVyqm1ZwC65<P5&jLh6cx%)Y(-!uCxzN5&b%Z!Zha6iZW|NGa!|Mh?VU;py6tAG91zr56^w0?Fc"
    "|Mbu5ME`7`z0tdYi*}as+7?sZtSZ3u76jcdX@kpN&upcnz3ob9z4_2B>%hTVTu-ZXwJrYYTh;ZWgWr_5ODH(M*+(a}%^dtmA3gs2RX-*7;MaeGMNf~8CTP9+"
    "FTw2X5BT-I;_Omi`*f%6mwrR<)R%wyXF|WKcW5b&-c!L{jbM@n@Xo705VnW*L%P9OzfYJv>vvup(cbp<1r~d>`g?!2_LZK{dP{wC@9v6=b~_aHO~x~{_%beg"
    "4O<)S={<Wpy%FK-v+Ex0=cLhw_xcmU&qpt%XS$ibkM}T^fA;l0^a~%`c2B>&irvla_;%LI?ich^g3XV1cI^9K9~IBuc`H}BU@-&mW_q$WKBMJ*8K3=bA?o>J"
    "Px)Pbm*R^3<fh%Dd;4OStliVHed4oz!;@YRKmLiE8}0@{$KEjWqAhOd{P%XyUmZ+z%-oK@c9jnJl3qo}syC_1KRcTD_8S5luD5;9UYqkS_7hGqv>Z<M{iVfN"
    "6@X9iDvR53Y<JT}d*xNzp52$8^~d7gE^GJB?nPREY?vw9WgjW-*q2Y~1@zvs^3Q&I%f8amo}i|-SG_xaQGbQ|9(bv>zdi!r4g~<$&Dopm<)8gDz103{%>mOJ"
    "%3}!NdIMa1_gKbtP+-@=tCn~ZA3o4xcnHAP7Qh=PhYlTm!^A6EJkA2}5&?LL0K7yG*-QNT7Om?Ryo%k*nm#FkJs`L93t9{$0r)Nas)?z-HrMgScIn1zwER}%"
    "^*`?^ov(JqqMqC3>dkdjyHnzJnCmAN_U^fBw?oIOJb>Q8rmT_;-JDKJ;l0f{i!Iu)r7!f#N3{4>esX4a*+$@e6fE?1yB3}=yDyD29@yJ1kJhiu05Et2c%>`>"
    "rY3v*gC)ju?6%L^MeAb_dZoC1#IF}?17IHDcz9gc1X#dSfT>1WP8!P%TKsmuH$W@n-+to;EoaV--ZJkSU&BV@9M3g|S(A5Xo+KFW2}U+@Fs?@LnAJH0RKNHH"
    "Rg2L)+(gSop{%cR?I*Mt!vb*iyrxe6xDnEZ!$+G5YiRN5w}X9LDT~*7&93{xY+OJacBTN)jVMGnqJSIWrLtHT{PNQ4>d7u?gKb$s`_D)d-1-HG?p@_?S;3h1"
    "(rvq&L;0s~)m++b>bq|L4`9Fmb6z^tTzp~k?HgJyRkOF-{sq9j3~VORtBn=&wztpS=_D2mUR}3jtMHMpEgqwVDTW1F04|Fgaix|XS@Q5q=~4R$m|>*F5~(0M"
    "M=)mtyQ*F)X`OZ%)As3h0R`i}yVg5e-r3eW?yQTIG0p+p%hrbR#nzoRT8t0@m}dlFo)LgAqlYlh;M&e!`RNr~>H6a^{$Rgrh80bKYi8KPXK;oK4#4|(*8A=T"
    "MXo6}PrAn`M|jUV<4<Vycm22j`qzKdUh*1wvy@ht(8NXxa^DJU;CZ__T1@horNuzv^17&-HDZG~`w6=!thZ?_jnD3`;$r%ohK(yMBLA}ua|kVdqW~;P0>ajm"
    "hcJoRj2A5QHo32XJ=A5i80z>qv8K>sO%#At@^((6#hk+hv}>l+EC(Du*iFyqW9#LoFkr&BG|UwkCurq@+j1bYVh+X$u0ycx!#=qkM)(53HG`H*?KOj`Sb_a6"
    "F;wuC!efmW{4j(Wsla-~%#a09PtLE<{>LU+yDq&7Ob}kU&NJRurc}>nRRR8ZYBT;4KO0l9YqZgN^O0T0f`2U87wTAB1CG9T2XE^iD>UFz_n4-=rP<l{O|LP4"
    "IpR$U1U5Q@SQ2fpXuur73L3nQI7Y9ZXm5M|i3!4A%zZP?{Ec29|Lq971lPiiPj<x@X!&HeQqI1ff4uS{3b2dlQbU>`(O7f~8#gx2q=jK50GA7&BBq9(S%@qH"
    "d+Y_^nU~d_7XSDcE4`QtYIMSq*!8)<M?J0;=e)43p>;F8y!b@#?Z{#Dv*q2)mH1=Zwtm~y2<G}E2Z?CG#@e~d<0S&{5?!I~mgy>fwvRh}-p&tLo;iuzdLWCj"
    "OQx_AqYVaAuEh472ibef&SA{9I_<N6_iJayU|IT2yB9nCT&{DrS_j*8kbSl#bAyGG&-tjy%R7ganXzY5A5{6OTt3Z$zn!t;I{eud-md7nHqmcdXypsjs@N5x"
    "i%^IzLV?qVE_IPLZwnzT693C~FOvtfxZUBf%SW+$@_Y6;lon{Yxyo+kA6K2z6W@0GEl&qJu}Au6)_b&{-+7TAqWv~RrFH8ymZg8jq+l%4l{H!#tSh_1SKDM>"
    "tC*fJhu(HsZ}iC(#V(Nmj8DH8!_s2273R~lH?k=y^Wkl6Hu+hi<)iew#xQeT+g)tm(CXKarQ(0qr6PR1dK3Es{W;bQ*p%Kp7xvl!Udn8dygij>PRT;zA13&d"
    "+oAk3TDNWh=+@4rBU$pfV#$(|f48}KWp6n454QI!w$Qq!Jy63>tUxl$VL=Km$-f@#<fYSlOYrEAnLF21II!VSv6($y0(M#K#~!_6)2x%JJ8^A;RUshy$rr2;"
    "UV4evU1J_LA?c+*U%_{PlVvUBI<%vOA;7OsxlC4zJZDc|Log`XQ&xh1!7E|@OnCVh8;v=%SjN1S{j|Q#8{0WreOqkQmu4l~z>}7C?QVxp7l1>-;42u|ZX{dv"
    "k9Ph0WqL8LeYhTUNv_oB%YdyWtF_r`Ubcs&F>H^pnGCXfvp>eTo3eg;Df^)KhivDtLc822{UGxeoE^??lK@`i(S+vgXyT{y*kKA5tI@u^t@MSIceUxUQ}8jI"
    "&JUQT<ZFAQJFNQr2@2A1qtHtN`?b5I52d@rxDw!XF7TD0b;AW+C$lPdEIT?-&|+i?z&mJ9$$nS*3l~8w4B8+0sh@lQ172rl&lFo(ANAz<j~O>dKXHN!246Td"
    "XH5_*-gb2ZvZefqfL%1)qe{(BP6%+b1eBKm-l}0%{$BQ+e}F4abC0J|fLFz)g)Safzo7Nv83McV3a|mlreSr3ujU`I&7sUu-Wx2Fl9#v5K>H46hBqo<pAal;"
    "^zOgCj7?m3eJ`~MeqV|0-YH1m<23uMC$xA>1fWN(G}?17dsouO!F4t;&RlauFOpqwc#*guHd5G{dRcpdQfsulq>)EM0DiK7+o8;J)>F8jFu93^7v$}cguiUQ"
    "cCiK>On4;6XFTcJldQna<iFT={<hDpX2VzlrlIRyVG)Ww!?9W|(@3b&KcWBwEI;y76IhBIRP`gim25AAYuUDo3vXz5tz@hA@s74;=h>gt;m-=@cHOc~v_UKd"
    "#}>R=w|yDrB|Km5*}i#f3{%tg9<OL|9WZOjn89Y!>pi)mz2r59S<9ctFvUp^Eu#3?J8a=EqXj(wwm)?M1b6niW&6Z|c>wK${Nsc7{)9jM&Kv;uR}Q&e-`?TX"
    "ORwo}Ggp)svu&7-4Oz!wxC`*BHe=hJ5~J6wCOlAMv@~MVYj1A1wL~)*#<~Dp9|0UiVi?=t@w+rv#3VL*U;|9gb!EZ5N*1oz3sy02KBNandTc}JzaN67jm8JN"
    "*Rw6YlHb3&b&hV7-dI+Aebqw`E<dz*D>1F{!1|*TXQXo4tJtN!gE^f<%l&*N2ctc>*d!m%qm|*u-S{CbSJ+JDqqj15q-->7asa?wBsM&zQ?WfF!+1eE{QV0p"
    "%n|{#@Q-T1+alh9>yUm!d;Dchk&P=|gjg=CB`zX135QSc_|t5VKXIc4(0^Lr@|x7Q_>yu6Hmv|UhV~m+G6I705uQF9;U8YU1Dl^8I$qN|lQj#(W&l?x;qml4"
    "k2Ls`=2vQrFu=V18b+Z1@QV||51S{)85c8mRqEH9KLfzq1%p#s>{Q+AOgHpHireyBiL-<N%o4kl8$ZEah?!i$T%R(3Qec3jn#BGhcx`h~-TlJr?I&m0H3ah!"
    "mNNmcZw0`q;m!B%(M;>N1U;B1`+8XMzuR1-Rx3Igv7i^|5SI-LN5$b2dvEV`$^FabNC1c3>oV-y;|yB`J56kCcTK-xc2xZrEp32`S@Mr>z)@#i{@JQwOI~9c"
    "t!OrfSBmgR$_=tVcYLBd9nN*5kML0s`Rk^Qiaop`u2RMKm;G0e`2GVh9sPP2dnNiD&9mu>2Y4R29#xAN_Og@0Me{%6G;cZ=u|x1yLF&qV7HmQRrO0Jz@ekQ>"
    "!MOE@EjTM-@Tk`k0gQ8vn{EN{(Oe%fpX280UJP-9(x+U1Iun{1n9AO&z<US#WPF7=B!Gtc`077&d8mXC!i!5T;QhqZCwn?`2p+h<yV#66s&Ge;vOV})J80zW"
    "A==%p<{F-_I2D_@f+bas@*c?suowZDD=z~qjsoD83ZLy#Uz2dvx#p7I{N^%j9SOc|7~3aGEA}%ceAw#Jx*qHS+AX(J4G&k?jlr!E#&T#~;hnxwdszHj8!ZN#"
    "f3aO~>IjFaGxI(i{Lm$8YmI``ilEo}^MqpeCwp@|stRm+6hP0u^q4Q(dJYjNaQAAHm4eHjZdS9M<Pn35CVcqC?*+gW2*-2Rv;lLd(~vu_yoZvFaPz1n=7@O7"
    "&KL8HZh^BE9Kv2n_P;Q?6u|e=&2f`bvCzWhEHghnA&XfsjlrLbsUwVM@E{A|9tSpF&72Z<S3E?)Zyugs##d}ZjqwkR^S%2O-1Grf9P{>K(<+!QpwkOB+OT{$"
    "v8N{C-~!<1G6Wr4Njn=xaIuZ8e83wffXlt~yv5nmg?kaM{~4Y&|Coi%=}*jAkzoW{Hu$a!-|G=QVv*wa-p&<n&}J>}zcL?k;~1HSRUbQ|<<~Hmh3m%P4pvZw"
    "y%(d=9)H436yy1}ds64X|H8OC)&+GX!$_Xz#G)f8n*~+Op~W&MfY+^k<_c)8000<Z0vI%Uy|+iNCsr;%u&^JSr+)zcMgbf@`IR#dZ;&jag;PuBr7&sZDu!Y9"
    "<xgq=u*&=|8?+}n<<yg4%Zghx^!G-9ZuiR-H^seVyi6KS1G)}gP5}PsKw$eXJ(M#eXMEybX8(&8dpdVN!&b{HJt0P@+xaV<1K6?&aLpMHjr#N(Tr&i7n?lXU"
    "h##w`U0UEVNDp?w>V=pOcr=yc`ycs1VsYVQcuMsgcu^kAoGV(WvRCD^Ur7X$1cCWj!co;Ln|JY{1Y5!@H(V|TX9bL|p!n-me$j(CinpEr6WTdUxOFYtJHsIP"
    "P0_c0ehbZX7XWXe*SAS;k9eCr&VBre;TkNSU^~enPJMC+agl1$CG+rg;K@RZFqry1;8#%x$SWNnWgfzO2zrNo)v4^40T5jGKU!!VY>Da~{t)sKW+SwSZ3u|w"
    "=Q0i{fN%3y#)RO1x6pDq>)BH|dqgaRX03pQ`7361&ti?(+)3*O<|@2gxUJ4TxI)LPoftmZj2S-Jjw3G(PxDIu0Itz;H2(+?-e>8t*=`8_NG&7!ZNdzlIrPHG"
    "AsZp;-Z_x(A`=wNn~M#etVK<Rv@XQ9=e;(EwzTw`W^JBXoZw>hV)wQdJkSetXaL|!N<TLj@dr#1@@Qbf^xH@LG=G-E^|_tPXm7_YfZM&Z2Oa>t`JsVjR9#76"
    "mUNe%xnXrY+l-{Z{Nd_E%1_DOFm{fYGY4te=Bs5A`{G~@S2<SvE@!Rig}QPX2_{$^u|xM>et78cM#Dbw6m1D-FkQmOKD<eEb1n9C$S?NzIdTFPK>@Um2Cyxk"
    "=!YLYiFr(5OJNWzf(hh*j_F^@&=ZBg0Ub)~hIg^8*7X=H%#=;Op>=WdaaBs-8_9S3b4Gcm3VcxTvkAb1rcS35y-%)ZA=u3xEzO2(n%^^<j!YfIQ<vVN2q%?m"
    "!=v)%Wo;6(&A$Kj=2b1udVI9y?AKZJQ2_WH0&a(I_^<F#2yi{yfNc7~=JgM7N16SN9B6yAa68N7?|QZi{;@f*F@&3o&MtHH%OQU=K@SNKKfl<6OAo_0cYS&W"
    "etx-GmY3T$M_*+Tef_M>k@2bfp<mrFqG_XA09H@+p2f(=!Z_D+Y+wY*b&$@3p@r?307Q<w>K$6{KB{-*<p{vjTD^nO;=~GqJ7_!Rte)?4en@@6rj;HtmQr7&"
    "^`z(xP?sI{*V}RMV;_o_q*m~vV<`+aGw_oHz^!pREdyKWyh+WQ+VDO-cxE|>!A7IBk)ns8n1E+5tecfMNpQ8AByK00d*|493}~X*(&_E5vTy@<wY-`77DAfb"
    "(LvNX`>PT_*tQ$@+;yuse1`tC0H2}T6yP@WFSgTP+~ZkRkOm#i?!wBpSJ@B7>D9Y<M-Wlm804yEVT$;jd(H+2(yhGm6FrIv+f82?;JY2}gLoa$Lov5#gdFZ+"
    "$_9%b=c`!EZ`Kfu#;5z`g&1b=E@C0p!1M^e`WaJ@_FU8OG}1n|O}&m!8}kC(`UFy)-9&R~mbdga2pBgBDz^9RALt@8z%XL};1A5$xW*VYn=Ig~6oAOGSIKkv"
    "D6Ma21ZpuE-r4j!@Urmx4H@^$$6VJ|)#JoJ&fxIm+?#*ljhO#>sV#aK;1+N?5TwQc{E~9=fv>vl2RP)u_kVyp@%b;NVvGcNW^qFWfc~Y<)fV^@6|`_q2_Q`~"
    "J`N6_e}E>+@jy@S$`*xX8ZDiZ%QW{FcD1DqGjK*VW$OwYwo7QSN-Ds7(k=znGXR&%gAocp?mW0b4x<1Rmcz*X*zP!)$39(p!q^ii3UEIvSHVmv0j^8{|BL|m"
    "RlLe4SHnRI>%J?GIR}=<h=-~Z*ql*8KJj<O)K_e_ha3$yZ*UQZnLPQI+(+9jUY=<!A5-X&nHk$arAeg7mw-X&%g%jfF17EAcYcRU+5OnN9lr4RD5s*F1_(cF"
    "lQMhr7B>I47m<Hvfy*L*vFXn~Mx*~JJ0o)`G`f7Q-+$#OxEa{Z-F6_2U9fu<aJyi$f1%^TC_&PSxeh?De&OCfn#XwC0|7(6Gxw6Gm|uR!+@h{*TipHRh-8m;"
    "4S=5BR|}s_YVzy=(6M&EM(efCbb2SdHkTIQ;>LXV$G4Uq?<IjA7>z+<fqB(`KcK~#E?#B8rSb|JJ1D$?UV`7K!0bZ<cDXuBwD1zUg3ag8Nv~^m#pM-_blm|}"
    "^1vEN1kTtL@$&)mLx4Md!p9!8%VgOiFeCsRpje!H?erFLb6H2|+^f=m?vGBvcM&}#_LXz8DA>%<AqV|Zz>Z7-h;dg7wqBp@R@ND`%Ge;WnE`$eFWUmU7bdHK"
    "Aiu&)BKRNhint*>rEl1n_@EEjGb^o^eMcuLdOvZFtL*|i5!Xt=MJa&mY%9f0lYDLPkM~AMz>IM?!YmBm?qMxsAL<qzZ+iiV;=gAO`%4)u8EhBYbpmcX_Taa;"
    ";Tu|B(nT6^H!oGf?bCq5f&jaI-$G7qS#vG34b0Ob1|dvA0Wbx%2VbT$cP|+LlJyOcbJm%|BNxP~bdr?lj?i#J{DD*=TW~e*P+{-_tQaLF$81-XPNDVYdjbT("
    "lV`DJ31ABeKy0G5K;(iOmi;EYn8A?latnF7BS+aj!aX%fd5`~kc(Mv+!kH(>&lQ2Op%6gtaV{btW=C*PgzXR8A?^cPRsE-Vkg&Pp?t)<~J#fJK3%hRSH@ofc"
    "Z~F)Cr1opD6#N%^d}@Qh3{C*X=Gt?xI22&{Fo2*rX{_BoZ(p}hCSU3o`)-Y=SdVh7u`k9?Ue?KAUY#Reavdw0S4v{C5&$BTKfAysCAXN{t6Ygv0W$zx!-mQL"
    "RE-H*c@x|q8A#4T*f7qqf``3(P8#PUwmD++dubCq9Mb-{hhPovf`H&^wg)`k#RI|+G?OY#(hn+4_X`d&=&)06Eft&rc;!=5m<_&te`&EQ37}n3vi<B}4%dn-"
    "OxO(i$ywOigLEG8j1Sn334qmiJ05T61^|cwE@#u)5iaWzjjq-hcV7TWKCLltXe$cB!mLV->7NmRRVFniFShXtZ<xz{GSvP$ch4<Q>FAeeq&;H}+)g7rP0Fb="
    "-<Llvq4h3vaNp@<Ue@?pnIEv(T-M0BA6>YT*6!T0;+c(si|N3>I(*886a&VuufgE=>rX*ujR+T7uXbj@3l54d1{i4TE4XW97WEQvq^wAL+mRhEJz&jwr8p%w"
    "^JnfpjFb;|B|2f0%2bK#pupB#0gMjMpGj7hcbm2Tg0?W8rNvY)AmSG#NJf2JU|tGi32v@;P5)ql=}9^q)_8Ie0qzC^uX3_EuU!3?%WM4?_ga7}T-am5+3>B2"
    "7Gqcd0!A{0s#g=CtNPp@M^1j}KiNcdu~|3WN9&AW>7E$A!EKcmH`=|_Fl;PDXya#R41vJ`j#&X%6BQgP&?>-2QefOC0Fa3ML4!JwnLY2ZK8A`nsKK)ura-&h"
    "k!U){icsOlJyl@bdb2jwCNoBCT`oq|O~rmf{tGQvRk23!K__#YEX}T7*#&_!;n$Xr`4rA%0baR?;3iGeN);`<Jqj>$R;ss4hdqeSSE`{=cW&ngL<AJjjrIU{"
    "t2g+B2*LFRh!)9h<;qq4!oJ&!chS<#Wq`irco+6ICV!pz;RuaA`5>8mjw7~Ak()jNVDJy@!nWX(+z=T1OIoZ)9wwaf6fGRZ0`S{|JA0ysw8J(03J;ioaSP#B"
    "5+mDB-aJR$h?%3Z%MLa(@L>O_u!#2wfP_N<?s91rw(Uu*t<loSX)#%gti9v5MuE!=LvPKD|M|j*Ewllvf$Q5wsr7=EZo1YBcpVDn2g+2iJ6J5pX{qiI$;HB<"
    "vE9Sa^{+VOoy>4LVr!F*=F$Rpixx<gmOPpJ9YieHQTmsGOWDg0S4>9+3OEPjIecp~!VCF9XXjN)j0hj@*<<dYVDW~pfpDZ)efW*xzy|Pdmhu&upRwL8E4LFL"
    "AHj&o3-FI7DQRRWN&2e6t_aM-K-25ei8dNZ_~mZb0R)5s@Il%`{@BJF7bvH(wHprzO|RI53-^BKzaa!U!Is}k-BI&tzPQ_UjuxJ%V7?>AZ1#o;Q@85awUrBK"
    "@l5%-c96!7;K^-lUzxPG?Lc5NrpxH1E}P0fz@>aQ#xo0Yth5lmDzIVicTch>1>g)Ihv-#a(_NN2f{-B3Ah|Ay7-ej4+#iMaW3SkTWJrFRJy2b=5MOzf-#<l="
    "m(75T%`kTwuF*<FxQ*e<2e|`$I9}%k5f&M)l(v?Z!OCL#KSQ*%mk#wHZc9cXLnrNW2THaqa|{~Rr*M<rPLHIL?$4n)khN!G&o!<R+&jyW*qjK3Lrx|~8BnMc"
    "=)tQ*{QPc?WXNt#1|bdw%RHmxAba1Dnk8=%?ftRV%sA$UcO-F@`}FXX`@s@!z`k4!@XV>UXb<W9Zx17%;Tu|7HQj7zLX7Y+1<kNV)!|@2*lM1N<CeKz!n=Y8"
    "TcWX@E|Kf<lwctEDS^3NHCHy(2yktiTQ;v^AL^@y&vYFRpYh#Xp@aJ(SAed<7!<I5P~Tkxf|m{4(E|9GAaFc;rC}*x4DoXuv!wvClxMGE-0~cYMBMiF*wz;$"
    "G1eCd6G%UuMf*sVAU!ttWdVZZQhK=Wh@H@4fcc#b*o<yef}s_}i;OiFGialb$_F>OhaI-V!Db4}MC?Y`<VqMARVfd%B~PAKj7jATm=xTrO}!4J6Gs}B*h-9h"
    "!Nyj!S_?s|+wLKX|32U=1?Mlca9IdI$SnA=qpvB*4bbB13BZjGe(qq^+>Uk3%w#7<Q9l8s1Pd^Cu?iO8>x&)zqnT<J0OFk7jrm7=B9?g?65BUwC_vSVKVkge"
    "&Rwbxq{sXK+5>}MnG6TKgu;_^m!i9Kmqh(@S4Y=>`>%ifucn%Nut)Ww?A2@usOP|Z0676mJk$`NsVfB{wFJN=a!+>al^ouMV!~Ah;6g+?2%GB?CC+ulRPefI"
    "!h-52fGd1Ohs-C|v@QI+2Z99J=*!5RWe<j~9<r#h9r{5J+&cnbW+=;IGv#h8Kc<0~r$$kGEYhLu3*4ip4K$X@zKBi9yQm_5RD@e57=HfcS%6nWKsZbTAig6&"
    "KG!0=Cx*xub?jdRz=x?l%_GztU}eDh8OE<($}EkRjQ<86TRDee<!dU0!sVKx9`$mi=)=MUD#JDd9)OzUmkjkyFB!~cvTq757XVU}2UD8&0&L#K4C%L0@V6_#"
    "d|sGBujrSL{yn@vPx9b%_p~eV3kcZn{*p}~4j2r^UMlquqvH?}IlkU_W^TbAY@cUic-!>Q@7kVF*$J9AK9dRNR{**Q&hKzCOHV|;N-#1ws)pk^dbqN{A@)#$"
    "<K0V}N9YG`zydilW<^U2g_Nt@gX2N-W;+kIrcbHlI3x;b5I@jHPRj|OQ+YgX3X=IB@g@Z@cN<qywHsIR%y&D?y56#fFC&M-SRDY%x9lCjNC|#Z%-oS7$pl1S"
    "0dNt!u6@s{ndOOlYFWoS0PpYsKwh-;l!v6I>}-ghk8r!W?;Kj#2L5FEZ~XTk{D*l+K=4DZ3N=i*t1H;zHZ9;6E5ij3gq-u-Wsiw6RmAgIU=KDu{W8M{*(#r~"
    "+%+(stN_MI<W=d2GLs*`UbBy@@U3cO)^PcKk2abs+dvfKh>3Yi(s+G&!qWDrr7c90N<mB`fUbyC3eH{a!IGFtVUWsPj<8|S=4|23U$8d1Ji_?4_+(~~ACZHT"
    "%i>Scw6i^qh0K8}hs?pNM_e8(#d64&ps+piM&=ns9CdWZ=<et)vg}^aBFrlQVFUp%X9W1iKFB`Ub9;w8+3490$wb)>hOmGz_QD?WI7)71tc}aFtp8*KfqW+b"
    "cJyo%5nc}N8jEN_aF~_hdsAgJS)XN4=Wf>|)V%`es<|e^y4{+@7uZ8&oC)|MU{-<hhijg}7^1<hoS-?WK+uCrkNJ94%Vj=VJp{`9Xc8pT5fA8z>aG(3_xA$c"
    "$Q}Z(Ute`sqb4l3kGMi_kvOctb5;W$dS(yQnRZS&`YhubA79bZ-L-q;WPf~hoh#TzA;RpqU!{g`ORGF|G(SrXq%07C1OoEApiXn!0k}w{KM24>Cm=_%66`)#"
    "<e3y2N<Ze##fd`0#VN>aKvu%?A}cM&VRlKraQg`18a7h$C)}a}JoBe2cge_83ZQnK<v51VWm1ry?r7LHikJ`>6I1$9n!0!}gStz)le<f@IRr#pr?8tLvkB6c"
    "#2you3g&ED0N0729f3yrAL>(O`KPPH^9xanw6f_00SZ6-wi|jQ^BJVU7kH+G4ubgnl-!W~6tt9Jl@3x>0QX~`Sop%ks2~R--Vp)<>A^hUy}-Ht2HF&P4gDF7"
    "ARFi2OPVaI1@77&7hHSnqr=Dk?Np*}52LhdPZP9yU=Q70;jz0N$fFV9A2$q1Rcaiom6~ViU$p0fOg=SNB-08OhaSQfR)8_1m3xKXbq2ft3D33I!te+9R~to*"
    "kDzEja32p!uOMNeC9A6v&BNC^@*QapvX@j!?(v1d_FF+QiCqPvA1Wm@vSIl6O&#G17v~$ky4&%3I~zx4er3Lt*Jl#U4bW%Mdxncb^@T7T1lTq44_n`aV$$QU"
    "js$N6VX8zT7-&iYo~vYpfekS(xMu5*6sB3NELN}7F!(>33%>vtc=={_p8$H`s&C}=RNt_Yn$pp>YdLe7z;n|raZ6-&8K`HnWu&38>0?=!7t(#ZDAH>?5;G9W"
    "m3`QI2f#G03^KFy6^wWYx4`e1Xzwk7oq+)F`U7$qr^M_Nc95EJ%NUwU^#X}rdSFa_K4Jk?5QXmbH1j>U>NApHP~$QyGCRkt=sIRRK0!%yB9(Rb!Mj$y(|fAy"
    "Fi;vlB6;)&qndJpJ%jFLPX#B8AK4$9T2TR((bN|oitU(80RxC9E4hpuoIY9haz3;>0wUYS#b;i#OIjHg<?T4g9eCQpY`V?BFG3Q!!kBU2eFhkx?;^eU2!t|V"
    "tTh54wv&Emj&rYbz<^P)sgZqLF#!i*r0!bFmIXvJ&_I-WW*c|yvHR$yU%Ye&q_Z1@gQ*-RfmF^vTtPr14Gpew0ifdUuWlVt(k@`M-MQ(2Jw}0)jUbXDxIUfP"
    "?r0WwJw*x|Cfm;0vz>=np4?|VcM${B3?~PsK!KU3Sx_1k0-Hqza5O$-!Fr?kLx7DL0q_%Zr(6AGoUQuFJU^=z;;}NKc<;t%M3@y^s|4q-h!d9q6^?{BkXAbP"
    "%)eC4V%2lsYfu}chm1l2mNZWQ7VGd>1BcF7@EcmE<tK(ys%2Q?-t`>$T2AnnyS>rYdYhnUu8!n@(*MIfiEml{{2;$#yvsfdG&JTUSoCm6ZUpz8iyro-ass86"
    "<pmY7rw7tWWDusP_k|2g06p$;+k)GI;^ITh_R{$$3#NW<mGR4V4d0*qk+IKCZM3)324p=95|?el0U2y2wAiyv`T}LY^?V0Xo}bJzT}^xX2gqYh6q)9vf(U@k"
    "MIBqgn-^vntK>07OFwUGX$=aSi;a=3$UVp5WR-J}0YwgB_b(t=<avm;nJIulnVG$E49}OesSY3iBS26{CPqvz+G&p`0GVa;0fKb^bdt#%Ueja_o^5J+%z5(*"
    "Sbp3e<zK+QS5l#+Zc{Sg7TnkuQkLewh?)EKZx8?}&Um)p`+f=E381jK9k<wF1-T`|6ul?15+Gd8eV`?kK2r%2kvJP9wK>&b-qFlO+eW!vRsNw9mX-AToyUk>"
    "cmd!}N6wkmNG(L3q4_rhDf4f{8I)a!WJhx7x&(kHPq~DkVEkmr9JED20ODraW2)2O?g`QUU~<p<cp;I{nc%~f$HC-{Btf&>!pC1^T+l=I-2`Cd)9I+>!8@wV"
    "ZM-RA5TVh0f?@d;X@eA<o5Mz0NW{G5nS{{g8MB%42hBwhET=A2X5uA$^J@+3h*AqdYFLuUBZp*v5#?v9MKfxRqwd;KAt2HV9V<|MDG3o_pYMx5HpfCTkF`%F"
    "?^RPp^x91CWVupr`xJa6t^q}?m;uaf<t<m7a#tw_8pta0uB}oeT)b1_j2sMf^Q5*&LgVEoT${F2tW9znqiv}z9#sLH>PzNKIQE!~G`)s=L~btUsC1N-;S{5="
    "_!Q%QR(kf0KR{og9JPTY086=w^>+lwjiJQGF0!;0IPLdd&|-LmrlS?>h?|tk;xFqa&QwYxc!;S2bKK2`e}G~s>4E6;{Xmi5`+?I@c>?oKX^g`H0HeO<ZSv-4"
    "v>4$xcxfKfK^s|B-g#krV|TD8G{63T|NH;*e}jMMw=Y=cm5bQBlAQ?U-DE8P*z=x753?TatN7ju5Rh71(mJ!e1>>^HpSRNq06TLxoHE;h<!A89kJ#r+4?G>p"
    "d$eaM%oMpnt)>w#<G}qa$ox)_#eT0tn;`q{ej(O=_d9t4^Iit=I-b?w`pkS0*JqEZ`kqPQzS}WTSiArka*$gv$nrf0Z}4_V|C0bW+rncY<`;Z1;e%~O;y>WA"
    "!<8*9JpT$7Cj#@bDu9+*K;Pc~I0AVRJ|+Q_f&5g0Nfrc4Dqb(PuwfkAf)uvXk>8<#_t&gwSVy-DScGy8eRJmqwuK;J`XlpT&kqQ8gt23AvBCX;yS#*o+#Lt-"
    "%E_hkheePukzPOn($4lfKAgSZ16BH%(!?)+`ZfD*ANNc_b}5rWe<@=$hqDxJaoCz-Nd|{aT8KXU$s=Y-X%Xa=9*}3m0QwL9^Ct@c7{$utMDm(S1<Qz7ptz=9"
    "wd7Bh1i4}aGRz_Yr^sX3JzgSUuQD2zv@k7Q&CHqUz+dM9Ftvp3B6%2nl0o65aos6Xp*?(HR!~moB_elX*Y$K^R<(K*5jP5*w8)X{rBmcvB+rp>bVJ|ge#32t"
    "rl|Pfp;4FSEo_rq=XR_!yU@=Ash^m?)7{93Uelg6k*E8baOWNWrI}wSx!N5VpP&)D%>}I{afCB{TSI&(_^E>c3JcNe?}Paa0Qz=p(51ywDgc5pAGY3biI!P8"
    "bNheezyIJr1{sTXkxXUj3MaHo3Sm(LX?dR?;tVQDkI9jO_#-F>*c@{I0H5-H&A{1y9SjCI3Uz~=fTS^Uh<VTC<en{Ts|wc}>49VGWrI|Wu01DXyxXU?vCAw9"
    ";Ta@G7(kiex+f*|3=2EXSn#sW6m6?BSOos;Lf$FTcg!wS8VUe8EmwleKq;wzsRd(EVh}T%+>d>kFT~c{V5@S+c#1O2NDtX!2O94AAzIo8i97jc(<6*Cs64(g"
    "qbjwvtE>iQIzD{=okpt6;hVmI!#CY<g%KDsVeg*wSJ-yvBgrSp6emdm7FZPEA3u=K1X(T>SpEe6-KLb^f|tLN8QX_k_judc6xV~6Hi^)i#%<x7PBFSCAhJuQ"
    "^g-l%pu*nv6_8*Nay2&W6961T{)H{)z)TXkx%?xf6Ej>TCC$Pvlpedt0?3{^9FXTq*|WAc5C9sd_JD+WIA9^x9x{p#c)kI=U7V-c_Yr{aqdlN^UQ5X0LT+uD"
    "d7?Gh1s)~jXM0PKIrEkPgIB>Z55R4+^q7x0I4{tW)OSLn54)#79csFB-|)M+@3zAV_#LsZ5@uSoZ3CROL*V0OU&8hXIb;~wdPq?u)x1LtQ~<U4xeRGSM)*{I"
    "FO(FGG${d%G=0a?W7{h20o&mRsU7nS|7arY411V2Bkz9Ayum$9PN;?HSS%-7LZB8nN|<wDGRFA@vP1!NOph)k!Oky;yU2742ZWw;HoDho2mUZOGuzc4yBG`{"
    "?J;Ga0yCBrfH%8ck-0Q}W(K_Rv#h7Kf6jnujPR>+k7thrd60fHjH{J0U~g)^?;JspXae9a$c_kKMgcNxn7~I`JYvDZW^DMXMk}$t0Q@d8!nL9tfGa531#lW{"
    "{X&ngfXwh;u7309VEe;EuoCCbcow9GvB3E=F09{Qb4{K<lNmLCrmlZZH?;DiKmGyCQ7NY(vB_&cB8OZ_6`K@DM}avIOF*bD_AtaCnsc>*$F>l0jT&BQ3;uKT"
    "v=-<}n?%axLxDP0Ib^1za-=_sd>;(dMT6femH<%Jba@K^?}-3bJD4MvPLpW|as}>wbA?FwUx1yaJw{;_02@*d87s-F&#@o|^)Hmc5UY%28v(|7P+%^J;POC;"
    "T=pK>?fi6~>BZ92FNdcWXlK0DGoM^b+U6Qdrt*7{?XLZ_8a7=;MjDnI=5?Hwkt`mgC>(%KzOm9BPo!Sk9?ZphAU60DCPR}R{|IVykNTia2jL&NeaL#JJ(f?^"
    "Rl8{Y4Mh4^dAh;V_UqlC@CMab_*6lQIIaM083Z6uBmn%Yq5a-cA5)V8i*@;@cV>n>y))csMpjs7%6mR0l_k>yR+ix-iimt5$9=HOQUx<WX8aad+<eS)d+G{v"
    "dpFM$*v4DaSY6^s^9xe6GP+{}a=fAF96ln|p7b#Jt(;>siL$;es3WTkW&i<Pn9dJ)(3Jjd!<bRn(L2<90;rI+tfX>Du>iSZ4K0!>X^ik`&YTG#`xR?0`-rq!"
    "NWG=Gh><>bW44wUfzXo2yC6G-u_vasjy>_Ir{}i_<3y8j?I0lSW4ac=o)$^JF5f_lLGFLVN!aULB9HlnB~`@y!+x#X4_2T-)VbJohG-*E)s%i=0X9!6^So4z"
    "DCo9nip9|4;{>1rih$e6u2rGQ^j4!LWj>=Oclx6y-4N1)oxXrGG@c98Iba-RUWCX_dF<qv6>-6DyA0#v7y0Nq6NnwVAggnoz04^^pT>hEvNIv0(FRns;M$`^"
    ";@V>Xva<odQ2@=P;|6SJufE_XE-y$nay#{5uLenEF#cf5lyfNxdzY|u%ChC2nh_1&eC1Q-Z<Mi$c^EW2uQb7IFMl#WcI$;v3IXFRIrET*w8R>zMm;t^XP*O<"
    "3eYrP3-n+|a68n)Vb@E|NVP(m+1xwkQUM4>Xku6!^Lof;cmdeIDDfUr*6I$DWC3ti$|2GVEx(q3Ofwm2wnEYI`UsMWmXv@4I+dkJEtTb<YMDRekvmiY-24d`"
    "A(PKFsyuN3!1@b-K!ty}a{n%;K^;~mzgn&pd|T4v=PluY#lw`hkNI{#fF@CUU^5Fa_n!j03(EF4FO$sGjEy~%keK3j_#~w%xyC2ztBju(4)&a{-UpaEyeboq"
    "%bA$&+;5iA7Xu&_3&!tK)qtfD2<tIwg5;3R)zU+D(XxVCJ_?>$go7(uBa1kSL+G(ofd=18x8Y~hTyx1XbOa1aHJ8X)A%IKO*DLH&)fynhik$OYpu_-0S*`;x"
    "SCFj^p)$rw&qG8mH5{AgA+96mAtj{(=w%vW(<J90s9+&Co=kGXd5HU{xy3B6xVPWYQxcnC(8|M${3iksLXZgxBMl)LX|Y)g+D}meu~$ZU=dUooHG3Xn`Lj22"
    "$YyWI-=#fe_K<%QJ$kB!Kn~l^hfgWikd<;4M;7py&tQ!NS5p4K>~;AQ^B$B7-glhhXf3=^g^VIZ;)ri#RA8b8|D_I3^ldi|5=r)8%y&-^L?ETD{0S$jDkC7&"
    "dfDR22SylnHM5BBzo3i&*$aSSw$cI<g#hm3MqM}-1Ryb{Od#0T2%uNt(t}MUfDY^8(FYmg(xW%Oc;qBGIWocE*8rh<O@I$hm2|dv4vS~RTP}TJBEjwA4~Q{_"
    "ywHBLM#Dh*GoZ?Y6F#PPqrzN;oW{+EsZtIUF1o8QNGzbXhWz2S&rw5qR}l<-2PiCIe@#bm=f&T=Q1O9@ZcGQSS6VXF=b?@X2icOPrQf(ZW=h6t#1%NNC=ENW"
    "SYK`M#dp9=HTdG5_fV%nUKlf5odA$L3K@!^>r=+01t26)rwih5_bmXfo7?HpC2cR9cwy4`(<6Dmr$?;R0`S=Cp$&LfD{R}t#2gt;6s%$pp}^0q`4}w&v-{qo"
    "l!Kq&2dhseW}HVE8uP5UgRPtZE`Qw|Jn(kTJ7fI&lTw|Kk8!#}CP|g0*bfgoQwH)EtaBp(?z?b!=kj9$;}r{lr%M1xMb=~Avz%j2;NcyUiIwfncGJ|n;DV=;"
    "7_MIJkwMmSAJhkjQXO|!27V6Y_h25AmI<b=Ri>nno(qObm1ODelwqyzl=}tgfmFXcB{`!@p-}Mi%#5t-K3bppyZ1=l{LT_nt#`<p5Jr`jyp!QGTDtg#&j{!S"
    "KQCzMOikDx8FbzcGu~DWTBia~Om5Y{01&_>UI6yOr5BW(Af>hRf*%5>hqSO;Tsg`LRW8DU3N~+Gw+P^n?!}Od!mE7Yb6x(?<!tBv@Xe`4tm1{)WA|A;N0k!f"
    "337;rM5TmmA;BWgBm<A8U$As2(jpEb1}Z$OssKXxzp;t72^PJoU%f+@dY@7x^La~93S{QGoa4TaQ2Id2Ll-M7*v<xQ;2>V4FG~P-&=b~iFs_?Qcq|MAeK+1y"
    "Rs<$_%l?u~CIIyA_Q4^Sdu9#an!E(_vm7F;>DrRv$^=B&--u8A3q!){MV0@+UkVHP6K)&<w_|}NrpU0IMVzh3@wl6z28#9+kH|g>H=_WCDU_>iZ+L2f<10P%"
    "WKK#B*`I1t>f(#G*u|>MP8lPC!2jHHNlneEOM*&e$7Mycn<DtQJ4U>*BQ2cWk#RZ!MupK=A&k17!tlGDEA&X5E8aW;kj|~AbSdYdYI#89{<eF7dr$#1o+^5J"
    "BrxTR7~A1^34ra1ySE{l|3#Jt0kF`5E9z68Y2^IeF+u1Li8$WmO7HajRO}O;W3gL*^ND<|;0UTV%8FpAHVXDz<^$Q`yjcs`>a@rBYAUU=K&pQ{A<W`pN9+Uz"
    "Ab*->f5k>7c8rKJ+$Ly`N#6WPAKw$BDEM6?!H9n(4Nd^VIFCo>K04m{#|)CnVy70Sb4)6mMP82B?To5*dDk!%fBXl&DHUhQ9QEJ+>tFwy>8-wP5*uWx{VC>L"
    "?HwvA%vbI)!C9hxhJ;F!%0g9CV+&4z#=f&@CbDQ>kX}rVQpAk}n1wE+F#<SljhZYiD2cbz2EHAan^Ok+)}@^MmAOz<PKAU~va5}cslBr8r+`Sh+Y6t}9}E9g"
    "mWhB&Y?X(iimUC@ChUH*6pqDhef<@7SrXrPGz2g+TjCqOZY`8!yA=T%d$nkuDzGqYhMxiQ`6r7sxkr)kCsyM6GOnX)m1?q*X97?mRlsGEE29><MV;=rMV&cR"
    "jm{Xxuh3iJC;O)+TEv<KK=>cVOK^<bE>{PSXoaSWm-?Z8YH^PQxo8o^^GZ*$c+tt+yhDf~xNAnz;8GB)BBzj6ryE?N^tmik2XCaFmSItkz%sNrQv#^oDvs^X"
    "7-<O=Y(PC6({H>>M&*H-L>Iaz1=;GKR*TtmADOM!e`6&ex&)KcsOVJ*Y&m<wE`b>U@<9v%$g8ld%*Nrz2>EznBL$lwJbMDbHg>rZ76Jh*!6t|DSfhue==G}f"
    "Eg<V-Cc~rz=l7ru>1YN%WR->;);Pp!9hC$N%FGLX(|-8zfs&|F4rbWxV$O$IlPUFn3S1y&O}{Zl86&ELR|!VkDmjY9P6=qozyotCryW8ph8U0v#4-m08$v<i"
    "1v)SIPOb9M9Sa^o65F_Xiz|AV&!>Cf7tjiNaL^rC<4JlzF)Sw-Fp`szJ5<iWx0ORsH8fHn6)C90$hl+UVx}MOVe911bLP<!fH=tGH}k3`?t=szJ3sKByZaIN"
    "_X7B~-#I*G!LPl^eGSSn7+nf1sjrI4&Xk9l#nPeZ3;E2G?@$PsFpPSzU_q&vr8dg5Oj|7rgHZKm@Nq4kAkmc`RvGA*!v+M)acoQk(C}U!s0~}}APHkoNkHaE"
    "4H#-$q`&<So3b_;nSN<tn8(27&&Wn70G<bTXD04!PhwfN2fIS`U92<RW1&as8L|{NW4i*(mQ#@8t7!dZ4$LH+IWRA-jWlV)o_)#0l;YXZ9WJ2s1P@e>Q8e;?"
    "Wk&APi(FMo#Z1DXJ^hD2z$)W{Exn<g#-k{x5oGtM4|>~uM*=fcEkvc54oj*DIO11#5KmO$8R|zoCup)B%#MB7l6N~BF;bR=XKBDhM#Z%JBe=GiiMsm{NzTm7"
    "OWTBVmqyFjZm;GY?kFL%a>%&juK3Ah(bXARus<|IwV8-6_n^5S<1FM!*S7#09;z|JgP;kh2TVHM*%HKF_zuTblt=oN+OTR;eH518TmNK%j0sa+jV4UhC5QH@"
    "NHfM-t%}bClorVOn*vEO`YGmSF#|&$YKFr$TZnC>hhnPT8%z<^mD%+dK$%nQjQFM%GMliFS^Lb{c=60UPO2_D5P<S?eqhj3K^}l}k?PF~?6E+J8@xh_qc2A_"
    "jqeT;Wn+yNKyv5egkLH*!n<s7=&yJx(<lirUyT4}*NHFuuM?DJEcR!iwA;Dt4{g7b|G~%?;PNcO%G@>GC4&wEz{=<@>9R=dqsd_h(z*2b8Dvn|!QtuGf3#ey"
    "QO`|mX20vu3Lg&Cp@IHb%_B}kC)ND}ODk^S7XC%TZOH!=fT=itBIjrRMB%0MKm{iNj;8q&g*q<<%Fnvgq4CQ|&*_uE_5ykcNvmSEp=-97$uoI|zm9f}mE7__"
    "vGJTC37c$+$zNOS;hR!`ODc!()GzkXXaz<S3kO$z`H_}Ola?x%(GzH+Dtw9<dfI6oLhVe!CdA1H(hCpYu;^U;mnrB4<X@Qse1iO+Yrnjpwrx4_icJgyEkZ~7"
    "ehpK%)u;QR&Mi;D8_B!UgIqCk4lRuuBXrV}h?H-Z09HANP}eAU1i+&2H$I?nV-4fX0OMJD+#H$lN+ATOl@iKv`uPO~Y?g}rFB>^-y#T80-lqPr#QfyQeEax~"
    "t-Wj?m{Y5MArrTLVL9Q~XI3sShP||?10}$H+nkVq3gW=uD4PPfs>I-@usKaKgC;pQTVmN^Obr6_yOD#Qa~Y=*{#wSxRDdAtZi$$YO4?8udz_=#Y4jQ8VX$BK"
    "GY7`5Q|3v^Bfse3@!u+uCy;e5gG-9;4gprj)5|UXW1j0YG-_e{js%EJKgvO03|{T=`zhQGxORK&7E}X=DgG^i@JWyW@9`VUkGI@-%P%H6Z><P&2t|DRnK2Wl"
    "n`YWlsJGdJ99Wu5ea+nHAhzz9+s^xL;jXJZ4#jvrACWIW<#A?PD6pqg&si@CmaIp}NWXyQ@-Kz7o?w=-KfU5Q2w)f(bmUnPX_dmKy7y`Ur`|hgsH&VpRP5Ns"
    "g$lNP<`v!cu`d-6APGBSz4Iu?I!KM%F&9Dsf9coFqj9@*<ZbPmAEU{a-a4(J2)=0Qi;~BDp9zWNeK3`zzTg6u_n}Ty6T2t*a+J$TMG4&mAV0$P-RnSjw}L;{"
    "efOcUqgQJ-f*@NHxFg<E8A05jN;_jrip3mF6Qf8-G{Afsevp3~o*qz{82do^P+Up*6EO)VR=aJ;T>%Lxs)&VSPSHw`sM0roWL>LCB1&krb}?L~br7%P5TkVS"
    "M`lx)518W>jL-cwe6&k+zJ~}eC?+E{-aYye&X*p)Z>*{Fl-%0w2jqHmUA>l~B9uJ<Yyt(yKq6?h2$GSQ&ys?vEYDUNRqP>Gi}WBd)6Z6O%SM_!dSQOHu282+"
    "4>O}2!pe<!zox4Hf?N-4q<?OZ#M@f=@e4E88`Z-tJ`vLrz*KaLPq^|0fJ&kzGwmEJDc`50@2|+5;voU@epa?#<%{Y)6xXR{=`_DDQVDur43<bhwxjRk@yeo`"
    "NX^q~U|jhH`&MzYN2hk#2Lpzb<`quv8;T#~0@5t2mN`dD4`Qp;GUyrt=(N3_x%+*M6oC-UKyIPBz<0<2DICwQNH0IuP<U7Xz0Aj2*!h51kdaYYbo-z+%NB?V"
    "LJzr^W6;3GC=M1dYoJOf!ZTRBW$a;&atUzDkC-IoPsUS^Na>sLb||L1^p=kVxTKwDgm45zPuw#TP+G1FX>o#od<0QO>yKin$RXsScz^OHU@>md(vP{_B6GA="
    "4nS$}W3Yu7<J0x2O5}LkOu&B?Kub4sWct+pA<9E^_$#jxj>jmqtMvmQD(WBT0M&{DD}X3L+rb%GUEj(wsYws=N$7iKqZ$LKw)-5%V&P(AlBZ*1@S#=9XdECp"
    "havWA&L89YOt6PkZDP7Zt>FdMUcy^ELyw5G!YWLpg~wU~D0Zc)L2PRU%ztH=u_%$8V17gGx3ZlEo>{8^w!ZXqC`M$at$2nCzfUB?g%R_Pq%VG_28Wai4Z(-*"
    ")coEndobGzuxhM9j=9%Wo@mKK<q+eksS~rIyvFc`DoF&zWFA8RL+c#a=2Jl#)xu&VZsyD_V!DGcw~4qu8;H~e(1wnWnGM-Qij1Q#)40?sMl>C*H*Qi(Fm5tQ"
    "t~t=91tUL5{zCTS-@U=btb1A`YD*83<0pSHS7;Rkvk|rU0ffJkd!#`R?w(LuCb%S7JigI}dcqWn&r~9UCpu{Hnd&W>S0JCDGF8r5+P*9M!N^ng1Fl1@f-tV2"
    "-~n3Hh!TK|ega^KTh9iya^)J@o7|HF8tb!6d!`l+djPmZ+5@&krWQP-q*e`sN&%B>o>?`)LiH+kq;|YRx%0L5r*uS=T@OK`_kCgJcL9*?B=fAebF9!A_kE!="
    "?mH@0oy-U3!jm5C-t|xhX{Q>j!GNS@?FGH+0>E1uX5GjvU@KGYe?GI+S))tQ+TjK1C<MUN2~+p-{s3GcmMdP~Y)bw?TS<A*as|b(sx2$XU0B2PrRTtmUd8^6"
    "|IC`M<e5fw6{8U?pk0lMK1?CDM9e~~JeUjjcGW06*?_qT1s$a-Q-qYNh#-@eoL>90CKQ-VC7tfDj8wYAm93ZYib#$#ASvP$^RgWRRMQqvU9d#*JQ8Q(vb~h3"
    "w2VY{f|<fbLF=DR=<?)D2n@SSs3?GQ(qYSdC9x!PC<v&qIE5_r0GJ!FSJj#n`y<7i#tqY)7j5J^i#7o&=Io+aGcQ7A5mCg4STTYH>jeji1?x~i5%A9C#YCPc"
    "R`N<Krt*pnl!`o4b@t#<wy?N+USRJMf`>Um64V`QvIt;Oswb8=x_%;b!dv-uVb;n+#g$m<A}Z+ij>jmtyt<KD2aUI=&c!Awa)I5FS%09pzQD#`V$}IbBXUD^"
    ")oo#1`?(?Hrhg6)D}nJ05Tam;^hEq*8H#kVnm12Hqn0j&G{|Z?Fp9MbLMN<|K|xzJ4Kfm?6W{mLhtmDRxx_1{k$p~UTbuJ=>t)z<tI|<pO+zRu7BLHFSmh%D"
    "+!Q`suu9x^BbdMfSogeb*SXpLH~uqe+7@e45gAO~PdqB_6sJ?uWSw4glq^Cy3W<jFAi>D^1Y4hRzf%P%kL1sPQ{8Frt7+IR)~qBeIshB2EPtjbKzrb%YNhyX"
    "S}6*_R?HBHjkSNga_Y56le9s04}fTef>8>9HGk&^uh&5d55`{vfbstRg)%7qOB@3`cuE9MW-mP2bJWKc#FoLso0lqpB<4<^Ofz@-gkk7+s1frlRkE~5#1m|G"
    "*a!G2i(d>=9Gu-8YlUCR<T;<l2<-(|7W@83Sc+w*+YP!2^iVPJioKo9ErlElIi*Sv8YpOfLT}0{9=#zvFseX>Enlhlmg`Rd0-YZ6SI1{8EHXoN=^9HaFKfs&"
    "q>3%Xprz-;9&VSbB`mg@M*i@pSS{laOJi3{P~6Dc0)4RnmPVZpZpSNtEA**k&9UsJtG&D2Bjz*}wwjkUJU$|0p}quRZY2HrD`eT7LXM=GSBS#Kzq}Mr7p6om"
    "X)v13^U^=@XqCX)6%Oud(7FqtfsjtQUnIUsk>?rhM+Kk|j95BMftx(T+3VKhsMg6FMX^xjTz|;w$;~KxjdDx6p9fY$OLzVH5(QAu@_NR9@l0va6AK0jfPJLZ"
    "Pf)3<d>^rcY#Y=$aj`f&bDM~5${Jaw>xe9e?GGvr`g=GtRS`Qv`q_85;Is#s<ePT!OA|<A!8UREPZUxycICIsy(pxD$c_L^3*kqLjGb4zl@?bGhg9nd@b}mu"
    "eWD_g_8{lWL)=@!-?nBnZNK(11J<lZ0L1_{?kbf%EdiJ#V{wN_glDWm)^~f^FjRg0#0JQjwGP+4U_K+=4S1XG>p-2aR&wc3LffWz_D@U8O#81<MRG0a(gWZ)"
    "tS)F83Bca2x?te1x<GnCIhkW=S$E400J$;CI;86Y5T|gm-^C#TsGA&LI!mnM=YCi$X8wEIWw750ma-LiqAVBM)pM7@0_lO<KtQER4KFC@&mWNJ!X2oZT-06{"
    "@H(el*XSJn^8|%v+%V26GdAbQMaDv`3S6Y57Jz+TVT57hte%CmSiQpDy?Y%00a6p?s3kpAu!#eZtS&t{b123xh;i6Ct>`_M(V-f8nD;)JqE4YL_En2zZY(MU"
    "x|Fnt$Oz!3d6nS4P!7Q~)_OPi4lfKNT0SywiaZ)kW>oo&@@RBf1cwV^FUebw-9gwJwzrV+(!jWkSpPAT1bYO|W0mWIO_ZF`F|Orrpb4F+Hmywz=A-~{{vqc5"
    "qx0#X;F}5PWe8R)Rqy_6`6o*;9+=rv02P8-iI@SkYYFm)U_J`#Z2)pv1ymLUD3LH9A%u53mRxH><u9_1wpc!10g_a=#&GV+evXMX1Yi)(_nd^K2SUHnYw%&g"
    "h<+U^V6Dr85PWKk>!SeE!fC~-BKNkq51t_qX6<jpI2x~D2n*n2+j@vdJ`+eVWbDa0Yj@N3BiTLOIp0&n`}|plpSW5f>Zb}~^Vut~*(q#&pk-vLk%lZ$g~O0q"
    "pGLRCfITQ?w98ZJxywiF$~=><${~{Q^T<V^Jrx4i`eNB2TYQ6Tl>fviUf$AjE&S#{iI+ba4X@o{F;bZ@d~()96YKEF&F*%E8;7JnD)l`g+50mSqRj`~L)ZKC"
    "kG?Jum`3fPh=Sf{;Ic&7l$U!)lrUJdnEr3iRLoj?C<|q43$~44hzvy#_^ohHuwXJr)#}27KBpvECA#3Zt7!MYbCyp$1kZHq7eO??zlQ52eC@lhZ@$llRf>?e"
    "MD@9OJM{VqE}4}UvPX4vfYUw9<guEo#ui@iNt&d}{FNJ-Nt$5MK!F%N8N!M~0aZoxosG4n@>`_H*6Kww)+z!sx&BL@e6A2=5){>f{+(lvg7B@$`kRX@-2;^t"
    "eVLaB@}2f?beamV+Oh(e74Gr?`nUAZ?6i44XfCir_dlCZ)G}3cV@Y9@6*l4)V6a3ILoowDU=RQSvP^6K^hoXP0n6fsbf)EoVFBqeOU!@%qH!DRK@uW>zUSEy"
    "j}nVG=RgtZ!u<9IHN=0!03an`P7;EqRD=En3G=_>B(4bPW+|aX=8aOHm7aDLQj7+5N@ZWm6wjjm%jhH0pMHdoYm()bS=unmEE1=Cr#%a`l!ws&3JB&?R8WHA"
    "z+X36EGB7#ybL{f5-k~(+eem}6R=uBoXe^}mYr5w>WRcShYvvjoT)i}2L;CP35SnN2vDhVm{qE<YP8(aLy5v$%ao&F4WIfEdRyd|kUv>vWAsiDkOA7ja+=M+"
    "rq3<#D6$gQk;ZrFSye%qL$II++cotan+-B&iB-VITmYW0>K8L3#hz%33b0%ASHe#KE0{~qe8JLA5WGKhsnR{Mz!UegpX2C*ilD5^nea{etqyas#kXh)MjIra"
    "cKHT{F!@HX$Prk{=`e;{S&1r4Rj@x7fGwDce^JfzBaU>~GFOm()44FK@8uqKd}I%fD<+4yXRlT%6Sh=6UT265bOOlG=nOH&TzSfT`{gM)f#oUl=f+~(qFT0A"
    "SAY+v>7g2w?C+q?!`l5|_jH<+fA&azP#rv=UKq?k0e+)MfW6qL$*eNcQy)V(%p|abGd9a&^fE_8nFcw$D_ZUfveQe9Zz4VBpNT5gtw^M~%%OY_u01k3jvEx("
    "5aS1N1Fy3YgC9LilYQK1dWy{pJI&|qP3qn%3*a!-7^O{GR*~p_AZdOiF*raoC4i|;YHQYEPbOguXvr-rl&Rw4ejVasWYkrau{rLv{FYrYJ!FF<Y#q57Z}R#m"
    "F!qH2L~m~UVtDDZRu@tqwq9H=7A#q}3)Q#X><tzsh-A_->8GyI53I?B`VJp!WGKGvU*Kf$nq5YInqAsjo0dDRs2xr|6I6=O4m0Odwt~B?hd_a=!uTot)pJ*j"
    "T<W9B?Knb`LFt4IEC7~I_}z`t*JfdDYH6^X+2@}{h>mTK{0<z{T2K%}VoZIpQ886kj5WQy1gl>Rc<S*FS4`A$4xEju2(~OD;aeMQVG|S+V3R8Vkrp|JsqN%d"
    "Mrx3?K76=9HH?9$hhC9atj5Gjzgap8ezPQWNe^;i|7HVFzkajW<jM#SVLmM@oNSjBotKbE?W+b^u4`mj5^-jhaP`3YGNlT$>X#}^*;J}<TXap5vv5ta2t{+r"
    "$f_KQ|4=^sM*x#fSOU%EpGPHVM)7Sq+C1?ksSO3o!zRVZpiN$rfh|cgW5auFh0jp?VZ$_f&jq@^&qGR>V-u}xZW+~8HH^hKxr1aFIw{o-!@WOjM!v@#b~Ik4"
    "%}j5t0@D7fSlD<90+>2r#`0APz~Y;|Q3$MIpGVYmgK9$nd|wL61n$?&$jb*J<SHMw{i&SbpOB&D2{A*r-J^Bi5Z;a<6XsTKH}-5u2#ACLW3QZph?p~2qRjNK"
    "$6w_9@n7mNGo**v3#T#o-}K~GhBenv7@&JXvKKABHU?W^gP$LM6j1}~cC=Nyb&rZ{F!lhDCf+S4G*Qgy7skg-rtubMX6m>2%@Q40g&JesXHW*K&phLqGB^tY"
    "B5|2*<bS`Je(KW0#!~=C%PvM&^Wasi`rEm}P)qR`iP2(A0Wq0UM|{cBwH0r{r=)->n__rI1i-q`^EV49kzKOJb1qOh9hrpZ_<>1P0b(d}PL(JB&4k*SF7eGx"
    "gead2S=sG4M!;Vc&8ZTB%?#ct!HUM6JTo5XmrN@YZ*btBl~?La=X2PfdRe9eZS7vj8WAm0G3aqji~SpYRZN}_OgoUTk%nOOgs{Jcc@{n(gXJ&7+9%{DtYYUP"
    "e}cuQfSFa9;Y7~yjiwQf=c-x8<X|Cd?|s9~Y+)64?jVtl>idk5XW9K0DK9NB6}YOKVfxmm<j<=Dx*rwSJFo|`#M2{oC<;<p0`q68%-PHdx7+bm`8|^(cXQlM"
    "syz9d;D7)b@`SYESHJDbNXO@2&i?V9KG@+M=>tPnF;f7C*w2R9LcYFfy{O{&D=N2F#rc9s2$xRubY?6=+)c9<PPy+*3Xm#Ot}Z<&Wt&QRNYixSDy9Yd5Cgh)"
    ";fD1OZ%mrh&0-$7?W<9W?JR|9`zn@i*KVL?1oK)Asa349jJp6^xLwb#t!+Q01<y+WtS{|BjgWNdw#xyKxZa&&dlLLSgAFGDgENfJP*6+(3Z2Jitisa%z+x)9"
    "KPJ$~BE*(M#Qza3gjn8Y#*}=e7p@=KM-+C@9w>XWj|_)M5Aq6UAHljtVN@*&b+IVaQx~LO6)>9x;|d+L%-dM#kcCy~Fg1(-<cdyBSUAw64&i+kx@9pApj-AU"
    "=GS;`kdA0-8JRdh!1a4^3Ye?ZGlP3AfTdV3ajZAiGlxDI;dwWEg>ft(N(|4itMrhD*UBJIhpQVI*FE=G%+SO`0-}1hi6DX4Y(eZz5`bbSze24u7EjeWLq-;7"
    "sSW|b#yn(~I|gtnAIu_C%uwQ7`2ZD6dYE>;n4yTXn8C|2S7}MZ)LM%cz9H61;f^YySrg}%sSzgcEVjIv!YKX|^Qqh!*4!~mM$T>q)wuLv;tcQmxF34R%u-WA"
    "Tl_O|rPdkRL^*-$_6$Mz+o=^z!!!3(LyufEuQr8aRn<!%!)?u){vJaQ9bEPlM%zOmfOE-<(bX$2pmGKa)^s%`^fR^5C_yDXHa!cV(o{v#_dMr^`f2D>^<<d0"
    ";~q+rh<V7%n19DOmP4@MOeCE`9Z0Ch{1>du57@`3B$`F)9wN#01C!zH9^87$%8(_LLHoiEQa~_&CxANn{DtHqs;Gu0^)*E;*Wu2eo}igVa(GwDQ56k7%g-Id"
    "N12ac#WIqb?;8GwOhk{HwUCq5j>ZVGHNH>`C~3`x(ta#ls;jmQ$7_Shp<~D3HBJD6a*Tsefw6Y{?{gG!T6(6)VZpuMHJ+gG@rap471CA;${#mDI#7U|(DxRy"
    "JAbJ3`G5bP{tp#DyP{3s#i?@kip&q<JuqF4-!7u1{g+*-s5O)4EzPc67R6R&YMQVIC6<RJZ27bY`4n;&cPvn$G0*XNo#$Mh!0*1m0<)uWc23tUY`I{m%P4(M"
    "E{yGX4$^NuwN&<#DN@S~XGAf_3t7yC_j7=#Kx~TzQ!{%M%QT_gH(FG*@Wx~0uXH)%e>BZivEBS>ZoSkeUE8Touk?naaH$0OS<twk2Sr*)Y|iIh{|<mTzw*4E"
    "VUHz;y`H(Hy1R(cJ%mU@03DRl1BILPSS~g>8QC;kc}ekk_6y>3*2pqxI?GxMMxBB7MJY<DDMQzC@_tRpy78!7zv5nM(5}<tS?ID%Z=p*vZJ|qlM-E9+;t(yn"
    "W{ss`hjdygfX1>}3*Wz(?4$Y>T<v{&SFhKi5*|5obI3_*_p4w-5o)wjUS>Fo%}ROd%>*n?k$52=+&zJ!to;{cTHM?$bD~Uj>RU%GzEYmP-BLb`)q_~kJ0NRM"
    "UN@GdJf?hk34#;yCfxAs=6niJv*lQWhS0YZX@1HEQf|zmst41RjP8R?R8)1i0`Si=4l~SkC1=i~I;<#&QB1)s3CAmVf&}=-iu<0pK@9~~nX~_8;62~t1Xz2T"
    "8UTS<0Vo$U@8OzQ>DDYk>66I<tSXN7q>juZaOOwAWY=?;%))|jt35FMk6OCb^dJIm#|*Ox%<9ZIU{_TW4ah#^V-!_#9aEpFMQQAWPLEm5pEg(o{49-EeSbJ2"
    "pEkiE&Ljn&_V5mC%uw(EreH0+Yoo_8t9g;{FFjvFtrh^9cj6n_C*>vH1@a{LpfkuYtLY4ojAPUDUQs_VL#=+YNLwgb^eP>G%Hjv-c-KczRrDx|{ERY4AL)(j"
    "ZjI@s9=<P`2jOSKtOr?Es|CST6Cz-h(E7Cn07eJ|+@TKG7cy1J`<O##8gvQ(xL*QX!H7Y~19;rhv$J`32UCUYVWaQ(oW@S9M4{jl0KWL}bacNBW@K2@{iieq"
    "Z(nuKDlteWOQPPjS)}Nc=d^!K>C9PKpqRA$$yGp3FxI;F8fQjJIb`*Aqz9wgA5MJZ6@~FDHU<K);A?f>I;-=-N(!H6<dvS9*u!Wh2qX-;?EPk%z&y@6lUU?f"
    "&p{r;Q`432`96s`Pd+^YFvsz!$>@>13dz^xvoP#)V7h$W&Se0W$GMn!a+xAFsW~Z-+~IO%F8#_Qs<8=hc>D!eN?&;`%Rfs`X~?3&`(sf4WNL=XJGs^ZV9!?`"
    "F|W!eQc)%EZ|pzKf>Av%2cNvpIeJ6e<?1^u@WQB?vW2Lnb#Gk)6i<7}FtYxVL7_<PvBdG=Yn!QB<q$%%FOem#Ju`v~vRzD(S499x`-3S<^vEHI@&**R>N#io"
    "tTZ-npIZB+_(H=V`^hxK(mzD@qE9l+1+W0-CrMgj7;1^}90kCq5h&K~dQYP2_1-I?EaWomphV2ly_P89PA`>0v5Ubj);~w@Vdo<<=k1A`<e;rkU|EN}{jW(?"
    "Gr-jR?-|Ecka$N%66PF~^UWWmhY);frSNiBuqSRkjM&&??CG=z^#BUfs5ax!UAhE69|XT0zABezk8Le)r^OAzw9=CnKK;I+LX@jkSkmycKo~xJUn6sb^nkRd"
    "FF_Pvz$wdgB=Z(ijgZH{jL8bLwC04VNhWcaRhok2ZW5i)A$Vg_6_hg)5G6@3dC3Z*ar!2SCOcO(o}b~@@XAFm_4}8u<#u?Aws9r@dXl9d8d^K_rqtnmIm(A3"
    "o7{*zT52Hkbubu1%qRe~A@AXEgZWfyF!$fX0jxVs^#ZHE)WB9lKlI21&Gw1Wm&~N2%rZy$fl)TYl2+~&<0Sj}m-9vbB)!J|L>d=;E2|mcX5-t531XNyTd(1i"
    "Jzb`QagE_WH^s(`CW|@#vL~L=)YTT=up9KsSG5-mB<zw%^QR}jd_?cFaM`BM5S{%Q>yehEzcj7?_R+mdm7;p&>u7B3@%`xyOishMCV+qDZ^WKLuVH8RKcveq"
    ">6S~bQuD~qI*xC<1A@(Za((qTzyxcqs~yku4{!RyD$AM6gP?7WzgMoa{rueDpRx;g<qsyuNwW4iE1-i8C2QHK#}qjxmDhwgMv>8TFw1GKoDO^7<k$>dopsZh"
    "5U0;Sk!3Habc4i()zeuODiJJE#3_M-Y;Ima3ueDd&hRv84joHNtpN4e<^>dHfSDvM=3xcM%AJf%i1-zZ`~Y=~3MHI*J3idN2Z}6GITRSfOpHdacqKp<(N=}o"
    "ogPZAJOLmz@S#MW>jPaH+H){#>M;u!VNlA!)D&>rb(jOF_W{6VqLjlfQkF$dGM7oDBrQ+^^HX4gdpQJY$10)OSme&4n8$vG^gy7vDF7w9a!==`0C?vr_aN&i"
    "c-$a`5Ox-tOUNb)Z_y_gVbN#QM8*#SlizhP$wE^>28#(35*5<i6ZJP>Ai1*Luc~FUeS=8@^Wz0MtiuPCMVVmh6h2mEpAJA~*kKYS`qxtT2r(*0Ife>SBbPUm"
    "sn|qWTK8B)LLW~IEmI16yB&7ZVdLt${l6rtUgQneghwb$DkqqBTXP{@*aMG+Ydll&9UCwJP-nJNzmbAwO%7qY2!2zrJ;M8Ea3-XO#KHVsFq|R75z-rZr#mJ*"
    "Lcm}<^xro~c*H8`=QmP?ET5^nAE8B2Url}l3GMkvO5%6UZJ7?qukYj^JAW*tdpnERk^qLTzjI-03xGmXa)^OLc?YnQ<>i(JLVKp`=uix~mRQJf@P!SvCR(~C"
    "wI&MO+;T$e9r==&XbCmavsE%|vQ@A=0sK$aZ;&&YYIgDD;%lC;-~5LN1z7rJl<0AnI}&xX5#Kpm^)Dm;_`u}x(vQ->0`RN~Ks-}E0DF?$6)C{Ar)ZIl7;}jF"
    "6H6-A+90=$S511&o?m{4JXro@5y@(j8APfi&&o@1S@pH}T&8&M%Rhkdz6ao2&0N`EkqS|a)3vdB@dl4P2kzW!AD7iKOBHlj$M2a?3epX&UA6*14z1v46qTVG"
    "u^Lh;h1NC4Og)u7F!dDZ+v$mek172P3rtUj=R$fmd=q4;(4PC}DBER;p56*Vpe5wO_cj?+A<#oeA-2gN)1d%nh{(t~w<a*hkb)z!?4vBn3j+8qe|Ba}2!I8z"
    "39(i=9<rz)cJ==B1!=LE9LxO10<av)IZ(6fAxktMfb~^pd(<CycX7X)(?S+^JG>$N6vqssYR{IlYFBe{tlYJ*T_9*3nN_QtU=FQaEy}z#C8*HxBp9g{wR07V"
    "(s6C0(_VF8TZBf>MCk_Ux59J+D0q^OI3A;XT?ZN746kJlpuXyBQSw`>log^kUlO1WjOGmM^PG6}K{hk$+ahB{wigWe-9QI3V0W!<Q``H>{{Tg0<du&E5UeDo"
    "k>}zrN;-8%t-b&-qZ3nR78u>Zm0$_RY@VIG(L+9YLw*_oShW0p3oK6QL1{WYr!&_opLhnrRFaDczL)?@pBe1zYixU3dr)jC`_=yY)!D4A3Ct{Iod8aM*?nM}"
    "ireW0u`vZ7_XJ~RJ7YlP^n#I~`OJ_nr}>B$A9UM&lP3Ss@^+6%SH`@Rhdc=yP?2Uk-lPzvQP}&r4ghs9iM*feBgvVW@3!r!kI*AG_qHR8!9Of~kcHD3$bF;-"
    "3I+vTTX?o>fZ)X}lB|U~kITq6@r)MpyDvuJ?u|W`j>M(1D3KwDLReInXDnKB2x9)QQ>1%nHd1-Y`E)x~_$M~oKd4iG2x4o1@WXZmr-K)3;{=pAb6*1rn7#(6"
    "04pc^$S){|FgZ&Pvd(`E5K0SbR+eptZCeK+=-aUjvmQW=Y4a=TpL{^@6xTSF39xhn{&&kgK}y~7*KL6CJI)@<a3MgK$<c(nscVw?2$vaGK*<za&TA7`#$Mu!"
    "HmmfQr$c&B)yKb&`S&(#t}pO6d9z2<-V^}lmnNTsuR#tm?VLHCUkgx%yW%IZKZyCLZU|c-1ml5{c~WMHf3{ooHgf>g+nPpqRD!YVs<YdkIqk^!tIm*t&!5#J"
    "U($uHncTyFn7^*M^_V<X6SdJwm434{6<F>j0l^Ovcs}@@NS!A~ks&ts;HoKt(lhhmW%#y!u}tvFG<xor`RlN~V^TZ$cd!5Or+;8xJ5ANodI7;h)7%YO%0}C6"
    "nE_9xm1TuR>*Zw3+M`L>j^4If3QuME$G3$fd^Cwz#FM{@PWtAFbd+lEA$oaHKkk%>zVLzX-{JRRN<#tNoa|ixPWb<u`VQpewI<lTydB)TpSP4(1;*rzi3S@m"
    "U>j^QHbI2VptOrOGu`t2tG?oE<{Swbq!T7|yS8-*W1#Xry4M=sg347{_^>vLQD9reO3M2`roL!_{2t|~4;W%PyfZxPj4+USc_acPA^E3leu(A@u!mpS{P5=#"
    "8{iOw5gzU!cJV5xr)ZF0P7XvsG?9vm8B<<t382Y=Mz0qvUxTZyRrf>6kq9uR0Rd!{xTHvBFV}!j)#VA|xdLSMDpLjG-})9q#^p(M#7+^xU~Z^^{}`M2AW0uF"
    "wg%Xz>RWO+J(FM%?5T22D{TvkL+^Zr1#W4j7CavTg3Js+30jasUmStWML7vU85*m($orB5E%VCVbltT%>bfnwf|gmi3Q;ru=>$a{8!U!o)|FOlvLDW@9G3%U"
    "333}EvXoiLPt2{7TmUv1nH49YYs(xhHxwDU*S$Inl4nlm*A{<k0jMAoz@9CxHslO{ea2Hi|IKRCs||~%`d>Fn7|VgOh{?((<D2%2?V*p~77}!*ywh<|#H7HU"
    "K0m%hd8v<T!E_|(IvC>>am)LqgfvlA>9Ukmv+My-yr~u=BT;aRnvnM2j=439Ff<AjzxeLb51liAz^MVUG$nq7)Ozj*F>h&NP*E(unTQke4B%ebCje2uSdh0S"
    "C&VApTS2i}0k~d!D~3wMV);?-;RRv!Fjiyky7b9KM?p`px6-i}X}#aynmdP|ptth#YaB}k>~o*Fg>M6YbpXH+4G=n2I9l9&lJswHg8<aQ$pgxZl(;hf1pu8{"
    "wb&+GSuXLXy?)^pX}a!YKuW`XjI@4<cewDC=n`Tvi<>(@+S?EE>J=a_y8eTT2?3~>&@(eB$J`0s23{iq*f@hWVlgj~0+b}A^TFy3WgY*LMiVLprEH{CmgO3u"
    "l0yX02W!B-Kw4GX82NA50?q?w!9wj9`MV3ZZQpw>%ddO*OF4nzFKX)4Vk|?_2Q-~@$S<DBp}%+re~~ni3R5gs0>)g#Qi(d>5_e0)l>T8mNn;#-?>B6H1h{7q"
    "e7{ARK5zF!Ryhv3SU~kOI5@dsA0TgK#EG1iJy#aL6KaYC)e+-^=?9h>n}yuvhACp2`-I~iI55Ur<qrjKNbZx2kST}7A-PXT5qpC?i+<&($1K5#^rIYqm44LL"
    "5W82nU-Zn-8OnW<FhcrNL3!81E2OR9fC@X%@fy0@IS5QaW=hv(QwB9FKwYO;^6@glYA#G%@W+D9Psc$xLzXpWa^<7UprymQk-R;eE!kCADDa1`ZqWwN!4HZ>"
    "y_cTvynrti+&g}M?mgQW)SUA{YHH?}@64%WsrUsT7+KH74~9H#g65fkuYnd1gY0#XLIIV6flW@yDj8Re8ALf)F%}50_@*{R6gGnI4!+eYLxjsC*aDTs^(W2)"
    "vt9Y6{K^hJ=@n@A83dFQTGU2+nlo8JE3JxdNY0TCwhZ?g?_5MT-nrd*Xp-9X7|nKqiy%jS<|5`P<w7H890_raPi_iTVW)6z7ddF)iwf=O4&PoVVlDtoRtp*C"
    "G9ZVwgw81o9^$`TxWs?C2NHk+w(TQobluV;%9Fx)nXDyo6*Zx@L3~PgNPJ5AwfK~DrDBQM7CBZxs73Zq$W>5A+U`PcB+C@lx2b-RxG-m_Tm{RFa?ZlzRj%Sz"
    "S4V{n+ycTRnQG}PmOiC+#AZ7p0Pm_Ch1`8Pp%wA!QL`uZ*+!P!g%(Wn2IPV%zbzd;W0AmTl|;q{$lh75QtRbd#>yjX$FQaLwhewK+lG6Z6F}%_8*#yG8`PnZ"
    "i$s>~0d&<VaK89Ahvd08NA4Dx(%{mNw|Gbe$ZAIIs7{n__Vp^+t_|G^Onbmjyu<G*7S#c@{g&WhSR@rMGK^)0L*B?SPPc!#7*4?*Ttvl=0<hQ#;J01Gz!==>"
    "bc0J1$V;UO<j8U!>IxL2U!=(KP?}oNnV<Nfeh-10BIQqVOAr>zbne^IL@Z3W-F7|8?+bQQ_@%<h+<$AK57uq62aq8bv>=L6zb6}m8WdADSkZc!o32YR*|j&U"
    "Om1(GSD@YEUvK~mriiZq%MQ|R>n^)BX~A*|Y%lVPg}4BwL!3@bhp1ms&8Td}iwgmY&+Av#o=KmF6fNxm0Q33;SQrR_@^JKu`$yi&ZUle=7^7FL0mOocr#2ar"
    "h&H`nG<Pxy=DH=kM`|}`s-AYAAW^cp_XPOQkZZaGEBKB2cxC0)=Ai%nmeHp^V$i|vhynluplIpS#V)|6dj-oE_tr+3Sk4n9udtIIP&&Mkg*mu>l8zavhM5#~"
    "4#bjA(qjAeAom?uG|jC{-CESy(ua)S`HdD-X3CjCJSf0sC_Uk}K+q;Vv^S4fp-rU9wE_Tnb>GbA@%T(_@=ez3eF5ALFaP|Ze}SMu>~CgxjjC5J2&}o2e8i8z"
    "EvjB7Je$&#H@|ap2|{W3gA`a6l_r!SSSny#340q*8z~ue<)|8P*(b794@pVQ`D9e$Lm-w~LAI;+11OMJ+(2ztEa}>=+^*apOB8>}so;pwYv?SoBvx#0{ji=#"
    "=9*dJWW#ob{KSndF?tU{ug9x;;a@?~IsrEGXy@M%Et?LnbA|Qe3ZXeWYDdek!4sN%vv%&O`1Rk}z)T|GeyaXabE~{;8;?TCpTFRH<{CL>+-MfWmRFK;EG`Ue"
    "q{nU=KJKx%?1pmtBRl*8|LHqI++M@hCi5Rw{XdMo9}pAnF+6+OUqo@dp9R&pZf$CdtEEdzrwlT1mW=gCMHO5t97}pdsAUOobHj)MZ9!p?p9RMLAX$NLP5=Vh"
    "UhbKGZE1S8T!z~c8&3g9J&-1^cVXxF7yxOKUh{*Q+2(!;J657@*?d9r2y${(>x_#Cu}B|oD#t~ZJ}nDw<%>M!>lvG%cqN@{1s=Y0Xh9vl9AyzTwSZ}7TnzGM"
    "H2FyWN*=wf!xJWV1jf9p<mi|N<wGqtE0-#Bex&ezgabqXspaZNl2!^p1hsyIlSet!A7<{QhSjllur%1P)&a3PUO^=%fV-vR#>->~UY7*F7ImmcKGx$Ve6!#8"
    "1p=LYZuuYkvLXZFI&&w*f@tMq-z^_$dFT_^dQi^>YRcn=tR2S<6V*`#dD?)CBCNf^!!8z<h#Z!9^^O)Edl}%8!ml>jNx#}&n<VZ?Bv*?~VoK|7E)fMLC8hv1"
    "ZeMNiLg;xcPub2>VxOo!R9m~rh}=CQeTPnB<rN-00o1~_lvQ~}L_xvw3xHHq0{RmIRPC70P<{>&K>5v%-=2~x9!uj&oKNn&5WYPCfbU$v3Lfe>ChhQWi82Sz"
    "^3T$IP}x@x?JE)^T)SdH_&sdLy~&wP7O@ClrdaW*g;YE<avfA2y<E-Rukjs<-5s+q&>I}x{)sI0Mv@~IPkPoKKn$#J!M-H`dJ3@yUP;y5-9b%QKrkGk_)c1b"
    "Sevb2nt!^uHH&b^Zjirm&)6>a!Eg_vda~4`y5`!|ui{i^VQ;QaDVgLq>6LPQ`eznj9tisC4yZ4c7vDrejq`p>5`EC0?kAk5_7k@NLh(5w!PX~_Ch{sIzgeIy"
    "pM}Lj@|*q)wR8z=3KKw<Hu=yuRMd7sUZ?!}PKp<AVM}eo-z6smzlQ+aZ%Xq|3V(Vj<ig-ITYR}t`Hahsc^7?ML!1!u&C2(mbpD9{k-DNMhdV(4%G>2DLO5qX"
    "fflD)K;&g^H$8j;(nZathaXRHco<P10Gy4|S}D+{np|_}FlM2!HU*|@B!6}DHHZmN9ckQmt6f-_=pn!o#N7FqtOWv43v}&a)=&uo`~>rH*!`7%#GSmm95Uwp"
    "QN14^(Yrz(6J)%?^HU^lG7hRE*zboPfu*slMginnW}o5gjLr<Ql*gd=ktS3ysKkMj`_t=`lTevK4zb{+_Qd47+GDw@7DU1t(85kb00EPJIJ`2}HN1kRS}hgT"
    "LxJZ*-zGo*3-@%HvM1-cUq-N?uu?2^9f`%pCGBJWF#oB?fOlpg+i_)Duw*N>!!x-Yf}z4IJm7Z}K&Bu8=2X8Qn|LMJdA{Pkm`5Qt`z!hpOjeE9jDe&@8`MwU"
    "=mee|nJAf;EdYMCB+H_;b0v~)NIbKTh0LW7xC&JZ0u(FKr+i=&2)Lv(s(_`Bd1(B_5RNVZ2;2$?u3#~zKD(E&=({}&!EWhZ8~}fMgWWs93A}^|rdTLIyjzmx"
    "`cff#aAL_PBAInBxa=$m_>)=B!61_*i9s?OT(h*CQ?%r2?A$K-qa2()+M(NKhvJAGwijqw@IEod62H1)`Qit4PIciS!+vJP!Shn%<0*DHqQqjtf??|fol~)J"
    "$s_<dB9|HqpFbX1wu`vf<&zp9%OT41WCnLp9W{IaAFS8!!DlW_&@lC!XFiqP3xXgjpmDuWB?AwXSP;DukQ;&(K`|1jrJLRJ!N?|~*B&Bk0w~;eORFNe<~2K1"
    "*f3|Cfd4g;rcVGemZY1_8VV*&g0}?wAU-H(Hd<G0vRhq&Js<{l1mJL%qs+r0z&An_1;($hY96@>frAD4p56#m|L9WagCxa!-}#9;PXU7UGc8zj$x#-8QqZ7a"
    "2<e6dV4PfRgO0f<W|~gqR=&B{PmX*WoxId1_IGNrq&zo$p|prC%e~(p=m^Q0+~4K^D8RR@dC#^SU1up^v~Gpd@4v~^D;D80amPy%Q)g!2<p_oaJf{jQVNd{e"
    "XVM25bpXr-&dgXTF91T}>lr*=0zhl5q9s<+r@&IORH(!X-UYDkVR8Ybxi(=@tx_jtT6%D5!jH9w{+GPPV#E8H`XG${nYzXVtEWXlXRJl#uj&t8$(sZ&qgvr#"
    "2%u08rG7>mxsV12?1hvX+oXu33ANPHq;aON4)s$^s9R@iqx_KmNXrk3d(zX3<=g=vQ@MN`GSx2)<Pz%VLNfXN8suB(<G+A*{6Oj1&DL+!|72Wr5r7K8T7kI*"
    "Vz=$LUKNVp<*yhf2qLB=xeP2v<U`2}B^QQ#uI39y%wTr{|6_R6i9b9H{i{81KVO*nqys6*oGJup1jv0xOQlHmfcWQswWv>Lh{!Ph60dm{J`1c^#!s~I>RV-;"
    "7+DsYXk%sIK0UgF2hFH}N@${u98~EEC17_^#`e!Yy)oQ)dZRSgZU(Aov3S`kn06Kaz5@hJ6!w<yMoi|O+jN@Yp=xH`8h*huBy1S`HsCMpS1yshO^m)}T&v{G"
    "@OnSyA#JFg^J8k_9GbKs3r`MlphVbFzMe=iCm7Xvo_LG(I3{Z<uP!pYs%KVq+%9fvuaY`&yh{i0F$u6?NC6b7ZWqrepVVS|DvTh0zT)Q(5aK~Df`G7P&)Bi)"
    "Ss$_Bi4|aLqcs+eat7}gt_n!f)~F(!8zUcEwR@gM04@sIb8A!|Yt!jSp&!fQbTc(g$HTmsscAL<I8B_Y|7nj{u>?n$0{9-ET3pZ<BfX(ajk)wr)q6v&5Wi1f"
    "R`w}S>NKH3rvR*Bbtk-bG&pUP?rMjtUp6`2w6}NYhRD=pWTDhip&53j_ru8@@A=kJ_k-mNi^yUz4|A{pkj#EmP_yiPzu^ZJ5Ln<<EtYqtV6>83oeW2%B`c##"
    "OYoQ|u)KQY5z8yQF#co2R&#V1si}_<fb)uPphA;A@^$^igQNqPh~*HJf(Av~Gb9VZfhp_=aMM}XsXde|Kub>hm;#;lsaM#9{Qu`P^w$)C7T<aF+GSYohg{Uh"
    "oK_v1=2s<ns=atou2WN;%uAwnWFU1C2nx&6&9{s63X>4CU15SfzlttFd%ODzi7^Gp-IJzw0<P_(31VB?)T9MO$=z4(j>K|Hk=|V}n8<89=RMS^khP4n2z?m`"
    "wVCXDk*(sb(=6#-Q%qU_e)M2>3w|EZ8O~PUY3r}=v{72C5*I5F{XBb6eLgddU7MCU9)iG@eYZhz42<Lzclzv~>?ixFvchG*_x34*AA7pjalBgcvO`I!<phAV"
    "T=6f8wa34Zj46PU1JYy~JqjMa*>oKRR?@D<1Y6y;&8O!Mf(v3Ho2~Ru-q`tZg^QtbYNo0Bo$_i6Q-5**3r|qmdk<METiFtX5$gU)OO@g2=$%j#qykmQ%elpH"
    "|43&RQ1qCc9Xu3*hcPYiV%%b^_`XqkNu{rlaVaOnrrPAONITFwkylR6fWlJwI6Q#27+8&h#e}n1<AAufTnQI&eTpvYwbg6<T+78#rL7J>4pn%_Z1YbaWD|}}"
    "81jCNlaKf->%P}0vz6-yw<?R)*F~^^$*suCmJT38EN)3ESIKhrl(T_*CN@D<the5fRI#{a7M+4$%6LJ>brgv|c2mlDd%Q8btCGDtO`Mke^``R`ZCNLbjLY8w"
    "_AUcTeQwbuy@nH_lQ~vJNQc8*X`1cJk&g>TNleO$ZDA8U=8zfU6~^SVqh<_rvL2u^X1A6N+RvY`P@74%si@bU%-zWV2jYvBK4g4eFiTpR0^FRs%S}L}3<)ZF"
    "6f||R57dBnK2Vpcie|ST5Cte+fV6t<Pt4=6eB^59b_5lJ?@XygzF3hA_cUXIvs}q7<>!tZ-WR`Ie=dHp{k~tKt$uFc?;`Cp<lu{?YfGSZRy8Dw*yR8E?-!oR"
    "mM(e*RQX90oLq8-rlYEA9b~c|5!BWXt=}l7c0^Ktl=3A_pjwMZ^hg3Q6UEaMpN^;Lsh`?7@cIj{+}+tTD|vbir*l}`*qLG{UvY~4y+({BNh_eX%3OH`n~LA9"
    "LMO>xHBsQN3T|+CCC_jfsBjx@m6vCd8h5K$=LFf6yZ@vG)q?Xg87*I)!#;cvXBKB9&!o;+HN$!((uRA*;UpqZONNqgM*1lh=CR3Tn2XSz9GF{@$Bi_@irpK<"
    "@VEGj81_gC`XG=g^N-5Tf-5B9Vody(K33Hz03|G{BA0}!W(<6bsx%iREl4ZUL&b=jO;6Q^BgW>JQ<7qH;1Fo-f>n`XbLJh;8tU=05}+S%cpFKu#bvZ{Z*Arp"
    "#U~(V7yI3jK5;(X*&UhG<Ulw>of8>g_CLX)9DM{7<>K60tL9w?7S{dA^%#q&p8uFtCcXpDA30g#^wq{ERG9d%fN0_euMASJQtoO^i#Z3qbsrO)Sm<Q{mGGqL"
    "y+D3oL+YtXlNza$Ci&AlMb!2CkMGdPbIVx(tTt6pubz)A=8gJH!*`~ZQ;mI4&-D0?JZ7<gN<sj|oWx@OCe`f2uq@}XU8MH0J--6Py2f#`vWTU7<Ase?JrE@t"
    "`u3@a^0+XO^FZ(T$ZQt<EK9U-pY0iRY%a6(eILv@l_be?@<YFHg`Jo8_zdE5QWjh%?$J)(|6-7%{Dq9z;Buq1W%&y`aT$9_blB+lA5}02iILu%M#n?JW1|D#"
    "z5i?@MwvQ;_fsLby@JtC-ujVU0Ja!m`xnazIZ)TAvSM%ca0X^O3|sC?j;e*1PaHyp_|nAtDX|G8MWqQR+47v4SMpi*C5VN@6mk^mB?Q<HAt%J{M*48zH7AH?"
    "DdzHwGaoPa#Y)87!~Hf#6NLP{;vVcnzVqaD%uD+<cUKqnccZA$dBTmYb`*o>9vI}#%xoV~L|MA@#3Lzy0f5{?FdX^kDOP%_x`?^*V}u+P1>H3D7Huc1-~d1J"
    "$jvsRCaN?d=AoL5k8Aenva|PEp^_uAb5Yx8x4mF&*ySxJnpmG|7ET_KKX;v@w<y-fjUk;$wcIF>xY^0mEfwpN@6E|`wKg}e^t)D)-7j{7?I!xKm&HCp=2?^w"
    "`MOfIv9bORRbsKA+FdNFiXq!ftf<uvEzS$;YLT~d>qf+vU4-$xP9FD_TmY6dsuW50<pDYIdJ_2ZqzT(V>1@oEayYj?^1CCGIk$<ts9n$p2Ub)=2@R+^TF$2`"
    "NM5G?Y0sLl%~cC;oD_H8i5%THPMQ4F(jUMn!-c07TV_aSY&ikk@fszYK{4fx+7!E7KxX<){@oAHC?A$n-H*xtYWSoZCN=$t=pvWY#H0e5TxUBH&{Wl^uH4@2"
    "fRZw~ax3Xm3oE^@Dk5S`LHg&ETNK&+dSZVB^;OSwswu=s3)G8A(OzLsGJ0EuqGm78&12j74NCk%0-Njg*ltdizWBoRnvY$`bi!?YKQ-J_LzY!Rw?n(#_5%Fe"
    "H-QZu+LWNgXIQg!!k2B15QS}gGp)4oEi2yO*5gv`Ex}~VbR;|b_3GtfXyU^q#~M40c1|I6=KGE{iJWb@XA^X^rE{Z<^N<(x>lK<bdK8Mm8>EerqsWMQeMA6T"
    "R?+ZSN*~fb%-Y<NlxGwnHMfIGj#{){Zj8X{l=KcU#%GzYLAEOZ1or|MS#MM^EUQo{1RGXstlzY0?s(Z>)@ZKQzBA*o1t-!r%@H7`D~D{@<U)~rom56a*$siT"
    "XPpec+J8hb;p-qc+0T)0GnqW!2BEF=#5ki8r$`W4$G8$cTzNAHu;<0C#W2;XWt9J8v+*{I`vI&qS6RmUuTyZH+uN9CdmgepY7Rn`E52j_!S6P>I84XMez;{@"
    "d+a}vSrWvbv0_oMxyp``mB-l+e1z(-LU?^oI%5G0*A*Ao!h6LEGyvRU#9WV@cIO4RoB#y6+*qArgu5<w*1<C7&y1G!BTHw|N0v^l)D~O~ayU4$yj<4HPoX#*"
    "#ws`=lw2X~O1=A+bTAyk5`d;OMNKBR!h)as&3rFkBa|eBvod_(V!z+Y5QXKkq&P&JQk7qGD6NShFHkKIdoaK$TUtBgsQ)KHxk|2K;6{oV1rY*X-+64i4gf_l"
    "1xT1Y$AW7=5}=(5<^wKoEmK;1=AU?ydW=o>OlgzlSbCGa_ldaF(reilGMHi0;bwAv$AKy>c1fySYnvKZZsyV(`=GjEP$UJ=H6j0W<N>|LOUZqSRBuu0liVYB"
    "N-Wrpc~%DP<y!cS1b9ev$hH2YFSHdz!MPUbj#UTO!aAyhn?@4Pz{{Hl#)u7qd>0i#;adx$s$|tGFFkN?YRP30oN|hfZLJK%&sSasF^2&APyxFig4GkxgQ5Td"
    "iR~XnlDuVVlmIX~W*l%0!NKb;-n`5Wc5={(1)rO7$Ved;lu;z};WJVV9FC=nH~7b-iA7~{RHm;2auyA78|FBQGr%u^xiT+R$oB?vC&OtrJwc1rG<|mngsIRk"
    "l-Z|LB~go!erSJ$3FIVD{sZY^yyC@B4N>9DC>AUL;+62q(~|I~^ns)?JHL&MNHHvrSbI_)!Fi&r3E3i>pll=nGBf27)j%VDd2M?7BwLyqcYiv>{yR#yM&WzM"
    "-!_TC*eRcd!~*GwG_ougv;sJEXGa>`mHGV)(ajOd{9cz_Y0Ucm%s%&N?rkY}96%N3X)ZUzU*JrBTv?d;^)}VO^Y7G)&%b-|Gr{i^fczhF2qLMcCklil_YAU*"
    "53I0IaB!2qeCWo90F|Gw;Gwl$u=zLSl|&-~pcB0R1UrI?F2fhPxOk0Mf^8Q7dwd1RS6*B=E{O%s5a}Fm5WGaP&0re;zG74CqlzjIx#b7hX93WkZ1hv!Fa-=E"
    "PywhT5Ib^)yw)D9m~QHaSxToe(q0Ad6N@RTL?@8_u!2v_gJ&{31&50K3BD~Py!<yje%j<fwsT6kKC#%C>E*K=y&LcHj|GGIEK<Y-VDNF9X&3zBJ&S83bI|dU"
    "w|=5aMQWsUyi5?8)tVG!;7L>WmB1MJ1jys#mK+qpsr^V<Yvqs8;p+*4)=XL*lrc>QPcIQ$l$9ZzQ<TC@*O*$Au6YUj+not^Kz{!0=Q99q<u&M(kaTF0*mj*("
    "pYPTOZut`m*+_E~fO<|hw}o?0EPwjhJ~S$_Z{h4YQq&$oJX;xVk)5VO+8+eS-j>!#NK)~UhbRp;eyQIVY5>f~%BI!a@GXKV$BNsvNzkT}u)9a}K>&BSyJhgx"
    "Ca`Hp03r_FXdSUE?x7E=0ojxTKne5Ip7AEJKm$@bV{R3I5lN0J?r1SOR#aDo4n>arcPEhbB&2cP9d1%8DgVWS@9Bc<4e3T6pOFHh<^3o;9G~I%6~K~10juXf"
    "87d<J$WvcD8`JW2i>qq40S~;}x;Na6DJm&F%{8aj(A}v(thvjy(jK|68F?0RP$f6YyAp?{QVQEx0q}0=AyyY-Rr<$20AXEKH_!EX!UZkrlCoH{3Y@QV030Vv"
    "NjTG_Ka)grQ39y+!De5YQ2QoL*;tUcAQ4c{jPy#m<`XJO*Qo21CQ_T<UJ*l4t#lidTqjFL11Agrs`fDzB^6e8dIVi$N4+AQNB|yBbvM~wL;3_iU7k6Mo&GDT"
    "CbTouO=3OrmW##M!1P1m6Fan-@n6~yJRZU~`@0@&4vOdHpK_dJY|Wen-%r-hT<{h@kN`v$RQf%d=~VrlbogUjn*i0jidy}fZ9Ps4a%-o{d^T4}CcT^%tYbMX"
    "um|)m?_e(Qn=RY`!8MvGmJ|8swFYi_zz*iW6~K(!Qwq6sUb92DYV89|cPJW?SCoh-XxUtoX~~YpsN|R};3qN+W93HJRfz?1v(kqZPq`5VkMm&NL|MzuJ>>v`"
    "VT*uLe=lwWVbCAEBF|DlIJYeP?k{*OwW)W~Ef`!S@)mpK_zye}(h~*90#K(E#8VI$*0b5RLYk0H6TYRw2vG6pErqq201(n>lRf4Dp~XtHTaO1~4<#Tlbt`Q`"
    "G0CZiSB7PO;!IiliKDnk7C&-p!9q8tG}+QunwZQgmfaN=>=U&!a*==H)Uws1b_DwZn<~}lJPBBWVT>ONQa9<-@3YBDp}hVU(Sb0I2g?3xnH(WO@|=nYsLv4%"
    "!6WrCzR$kXCxADjV!v8%!x;TTRI0y;2PLGVj9J2D%O2@zd;$9<h#3T685(w?-=nu-R^5IX+7?tS(45iExFAIPOq)nBiAL5#+MOHSOwNtk^79$RXNo4Ha$MgJ"
    "2{-xWZ|#q<pWiDDz{4wV!7A=ya=k1f(Tas@57qtr&J3Q*B1qVsw>XjbSO5Yfjg?!sK61wwZAf~RyBUw%0k60f1kiz7xuBd?0K&Qk_H05_%<1_~$yjKuc;)2$"
    "ga7`;f4=1=2>=nd0Av~n@GNCeK$x;oWf1=d|Jk9_Z_T$d+H6aV>;iZYMDFJ)|J2Wemr4Ls%mk=JrmU=yk0w2<=3{%zdX_IO0AsvwjNp2p6=ZwP&;tk7**sOr"
    "Hw>#m{fUy4=P$%e+*^mM>05_MScNb7X92(s*JuT%;Q9S7owcbN+5J*AkfRBJ-bGM&fa6mDD)PKnTTjhucgG&n%@9syzn7K$z3QeRF(El7YglsZKg`*4QIJ;<"
    "C<zE`i>CH;itCYU$-V9g;4i$EP+F)KcwVn$+EQSN!~!6eE#Q8b>%3$WtR0*8>^f0DEw5Ph%j(Jd=mLPSD6j;*pi&@1RPQ~ox=*p7&|GF+w`@zBLKm+x#uI?;"
    ";7xv6hhSMznni?ndUpO*53fk!4sLtw5){~=;+`k?eZ|65Wa->}g9TAsu^^vIeiU%4`yXx6;fZAhIiGg0w7lhBk7B-~EHg=y#s3Jbl12K5lH4Zx=Ok`3SN9xt"
    "0m*ZaWM{Y}W$4mu$JjRb8RISX;sQ|kDM0?+Z)>VkN&oJ`O@5-d8L6rAiU^4S3U<FfA|WMcRS?Sd4kzfAx~C3axdM%ob|R=V=q(nCAg`)$j43c869E*PT2)z<"
    "v#N5WUsWm2rG4xvYm~j>9smJ$R?Sq395gFMSC%%(U+N%NimY^dnv)y8U81*4dLr|sU2?Ji5DNt^i=^|b6d9=&3#8uVaHQvm#gsbT>cw)5s|PGHgOrU9U?r<g"
    "y(g>ko!6;;{W(OrZ_us=<usa*;xC7=*m7QHRBrT%wVVJl*T{M7P8Ew+v~Mj3{fi^@;7$G@D1C9$RQlqNTF3?_zNnA1ZBMk1{K4`~*%KQ&ZTY8#xCo{@ZFgeN"
    "*m=Mwr}xD&%gqp4VDed1B3k8{sU-lhiB%rYm0HSJ8Rqdb-%sWh%nt8H&FJORUcuJwR@nt1Bf;F=D5FJDHIyt@)6ag87OK1OUuU{r1((I!6K6=VzZ`KMBqGW*"
    "foe22-}j18p8i1PgEpC)&f8SHpI!8Eb7Nw$oqqmC%A{(=ZQ9cMw3XqB<KSr<X|J+Q27nYgN94HwhDqp*C4#hlMdpi^SKY%d9jqnfEtQ_1ugLdSpqyMW1djds"
    "o+C)H<(nF`bU^8p_Ou)}1p``ak3+Ylyj7K76krRMP5otop-RpcTpMno#ZlhAsNk`RQUNc1MvAq9>#Gv{f)lEBq=!6}gx^U4Jj|&il`O@ApHcwGh*C+^(OKtD"
    "c81^b%hpGU3km=XQ~)B1kBPT^CAfg=V}f<8m**>$3u7s~GSjJWBlGU*gnLz*C?IW7PGyO)z={BRT#q}(2#&h|tj+>Z=WyIHnN2KB3%=LP@q7D`f9lEuHHW;#"
    "oc#%>+zlcf;i2#DZ40?FmrfB%M&_nVzrbN4fK@|_IMd0}FUTNOKmnaNllK;JkGJ9lMI!=07w=`~Bni*X8G^~qNgR;sF%lsF;tr{v4##^G$vhz*Eg($92@n!G"
    "KL(v=rKv%{Zn6uXZ5)_vd2>#-u9b3m&rMD8w`~8QQ=#XrU~%5%iTS;Y9XS!I4Jd*KzmQleBH2R#$VR+UjjX@|ngm+4Vmcu1we4Q**~}KmJiog#RdRO?<0u7>"
    ";T2&E0SJZr-8PlYx^2cdG8WG0o`G3>ApjW#0#a}ecX6kAtvGJc;58BSEyX?2ydO&_5AkwcQf*}5Vy)_~WMZFaYg2DK^fq8ce8$rIewjkfEKC;htqQ;vQUJV9"
    "0x)n1fU{ZvYM$NZ-rGXjnUpnN?h`~Ye&QHTW&otd8(C)Z)3=+qvhZWs|IFVHY3i5B%FG6_AoUp}kVX;>zi+EQ5;MWrz`8l`fgiaz%YAWgC>HxxgGbvBHaA`Z"
    "x#9~5&1h&oW}%J3F-(F9KaR3eH{tLpm~EIUHvfj!sT)UDVVT;`@iKNB{xVHMws@J^1k%T<y9LPa#m)&@{?5Z;N{)iIPBzUyFq_8S&O1M#L?Rruy`Kdw|A9E0"
    "tf<7Fd?J+N)gY2`#{NNpWoHSHrGw?veL*ZEe5;0UkU9H;1c3V#$5LAWi5kU%l=Y`L>$2j|rEEuTr8aXl*X5v&!o@9omBEtou4+M;>9{4W!*L6zmjCn{zG1A}"
    "Mk1S!`1$mx)+9QQolsU?tDWCHfTTmuX4OpE;iC=<we#dy5KbSroFJt0=|E6I_`4iF+Y_ChW78SF*;ltco8#0b=)sQS3%4(j*J5lDJ9CY0UvwJ|b}aXhL#!f0"
    "0Ln_k`6Jg?(#PCK0+7<Fr?r$+wY-60wu;*I@QLKyV$qd!tUwQBc^Xvg>0Uu9Ysal^tV#vCjs5Occj|qgC;@g(g(y-@KeFILMN}=&bIb)sM5~>b5M)WX?VarJ"
    "gN!+-CmDZYcf};l5ac9{Rh-vq1t!4g?n>?ks;M8GH7034Yvaj9`SMLYy^BL!)M@|hK{qLY9HW&bbC7=a^x{^Q!EFW$cFy<X>-_*t$UO?F6d;93jxwrsJqkNF"
    "IrF~CJgeg?mxy9qLdW+N$*A{p++}suk~j0_LA8zNEH!dFpQvz_?W^}V24Dtn=aZ5BNtHqdx5qmK`=kjpsdAJ(tpdV#0(h$wpte(*EMrFoaOwcA>J&j+)!{$X"
    "&URO8)0&^|y{*{CQqbix$P3V+h>2ISE03?VRCscsPDh-hsDk$gU6w<FZFfQB4oV#U{Q9r0+Y)ZMEh9De-`O9CNr+uN>76U%7Gf_v;9w@O%7Lk_4)K=3AaBFk"
    "hvkJ-*&oTE^D9Jd#1f^5$w*{B;p#n%p};o|VN>mlWUp*QWh$TYag)n{4u_j9Qh2zwCJ9}($Q!Fu50;j;a_P|%Bb|SCRxI}cI|?Jk&Kw<Cf7r5H07JRiq6*>k"
    "W~fw_x6CJyV?oR;9a;lr6hKyrbQm{y86awvb0S<JJvX$-U#GhuRD(!|9!iIk9?FYXJ1F^j-vi3nd=HpxI?pm5ZyXFk(gNYHGjC}#+4+RxV*zB)QLu@?4FF+L"
    "0UR#nD9ba}KE>!L)B@$+D7Ym6iJ`eS(xEpt%p*_LJ*4vQKPb9sOI5FCbJeWKNL40He?unikFXv}N7P+uxD63l4eJ{j0so>4(#klW^taqZf0khNh%})XDZ!Ml"
    "`}GGNECCp-@28E{wSs2pw1ID3yTOrNdq=97Snw!HAGnCLGnC=Q!tLdT5eu={m!O}5Z!AAnl9Jn;rS17K(qz?c>1BRpr>RuOckTq1FQi?$I6B<7pAb>-4oT1M"
    "X8}wIILJ;09+4#3HDXsX_X$}12E`#`)pCd}Xu_A8k0DGBu?avwrCue#kR7{XWR%X~QxBEB(n^uY*p<0Ev8#uqWVtYqKT02?JCt1?Yu^)^IvJ#AKE}I5l1sn@"
    "{Ye5CVo4+!5f=+&Yvow;x+=haO!_oZ(Rp$_58}1Uz1RN+U{>OC@1hj;l!AhQfM9o`<p>JecG$74RQDP8hUTnP3d(X1Eh2eqznTI|#S_3)!gS5(`#OVAs9QKe"
    "Vn+azU%MMT>A^2^dBs8r^XZ!TVdbXY($0u!k>w`l7y<sdPJm5gxfyK(n&hF8V<EmSeayEi=MS>>H<lbeQzeJn2?1DZ_A=NEC_suy9$Yw|GK^!vCpSEkpYmH0"
    "J|;iOP-5BJvY!X_l)U9onN&VphWC~OC@|^a*ayBO+)pUoCb*lG^T>iANgaE!vxqDALJp_g3yb)3FW_mD5f7==3d|3xz?6*rwq<+{7sxRZz~UCMq;CMMW=to%"
    "`jr5FXaS~P;XYfKU@^stB%J)>6?r6Hb_K_|?=&bzDB#v3_fo<f&xtu$uLN*!ESBxe?`HhoFWv^pD;N(2lhav@pb>K7p2<}!cb$0_1)%m@ErT;HcAKdy=PAx6"
    ")>oXO`ifIDWSyds>J$x7C$E_%KnT`x2;|H$)P$V;a~pq`83#O-1u5NI5snf8__;Af$}6@OdO}3|`XB#&1Z12RV>~`$f!kPs3jM^Nu>X;@KIUiv?zm_S#S^@h"
    "hX_DM8&7Us2zI{OqqjIJhe}kR927@n(L4Q;=W%g_6IzqrPFo&=k?pl8%N<%w5Ka!q_@GBE2*S4>&ujyi97SG(R14J7o|V&h{W|wH?++@~^!|WAkqTLX??jea"
    "a1uw-Rs!VDj4U^KvfMb9s#}?A$)1^<(0gLQ&43qYBC`wtWBHe*dtMVPUb)|>zJ^_M8yO`*kVmH1gvxyR2{R7Q>u4FU#xlUG)q<7nevvWo(?!aT0B9qqWe=sv"
    "tlya3Pj%k3hb##Z#csS-USq^<Nn=DN=wa2%+sCz@;7zz6KB#3od&Yw%Kpr}K^uD4TxG#8Y6@b$3>mkaM`*JPG+f95h^p3LRmzcM#0bt(uHXWn@Y7>fHHXYEe"
    "xDO5-o&LOwS5kGX*Y4gjhLe|Q*k6O!Uz;{_TEGl0mZkYsTQlFBSx~MCQd<_Q{0tHE7CT43r=-l1wh0*rk5!a>2&QODLuRfiEnrkq%M})89yC(ec!-6+qx4yP"
    "MqmMejZN@VW`!F$HFK&Ij>8YRDCawe8YBf#le<A8LJlrk1xDZ}=V9vGA;-}`I+roY=D5)kV6(q;mSr<6m<zONSm39hc^(kzsKr=u6<8$G1M%@^5w3PWK_MHl"
    "$Ui%O^}krw(<dyXKAODUuON?kBX_)|zR4@4D;HPh35_+^{C;o{iqW^GcpzI9h`@*iAvm$PU*@{nuU*q2^6OhlgVndx3qO5PgA;19`?Uw<0XYOIEYbn4kop!Z"
    "jM{{JS?LTuZUb)V8H*n|BseYEQ-%Ud3AI@%iTslL`M}#-4zwHyIXQj{v4jr^^kE@TRh9>RoEA(C+6N>5`GAZ=ZGv-Z^2(`GfL)saw>P52_Fn?-4r+skc;%y{"
    "lwHrXfFfr>aw!4aX-gk?f22?L$Ue3@4IZ!<Zs9eI+2fNeG1;QtSFJ}|bScdNs#UWazhTRyVw$Yk^*$aJ&F97^j#kWptM_FVi=-a<p7A59(G>I)AOm<r;R`)O"
    "v&_zOho`bzOD)JK67aiZXWLH+fH<ynMu<<ZErudSN{jftI5nPnac0hSyI9Z5s?SX$BGqNcEkQax?SpWrG(iWW+f~0ny1-FU-lAA5(Zi!^C$X8RHwt#}M0dHu"
    "k){QhQ`dK7ogSGM;vO=HDSFKdo%jN<wbb$|<N>cqrZ`@+l1D%sI`L~JEJ|nl=H<+oq4cw;(YEGZeszdcjMn%{<+E^w`l06XP_Tv`QHEj<hlqPfKI>pJVCy%0"
    "t^=U_{;&R1EcCawew8CiUSE*i{u=0x>=kQKJ<!q|1#sw-Go*N6`1Q_HwU8P7%RglCDnN+_+8}c7lXp$*_`4RbBq@;dTT!~ZhF|^$Ivxd8klJt5tB@_it0?v$"
    "X8m(F&`SxR(mV?qQ!GS3JZJ@oQ$`um{m?{aWUy>d$h^Ho)K;3nW$3ngsCT_zi=gC?zXEkK(g&+hIX}Y#G4c+`;KSvpd<4o_V-I9-h`q4LU%m|}nlBry+>q->"
    "z<+$gPC@#(IeGkJ_!RD>mRx&_B}|vtZPCMlTu{khYLAlFzj19)|CPlg0laDTUnpfMXmkOXUSI#cA6EeSxurB)5ulPYAYZNiE9({vBYF~)uVnKe01Drmkl0g;"
    "Ef~atvTALzTsL=-!M7>^1ufD!czi}5SqAX%Ljx9!gktebgGel7ea_~iU|T*&vNN_ta%Sv<v?+Vy;iUpUbTD(TNjHgYX3Jd+bTydB;jLHritO7z5UD1#g58bX"
    "qW&xtDYrPHmRq4IHhQHDHY3{9&HVwlFe9sODFX>`wS(6G&EnIU8d3mdfQ4MHf}7otM=JJ6Pr3_U-~1D3s%xB*nq_3n3qT@caD75np8)T7gC^`d<g+k($O)O)"
    "iX!T62NW&tnpK4YNF&l%>GnikPbkS-Q7QSQ?}PVbP{kS>vTW|jQWd|NpgR>KB|!&O@9hl->aWupfDlCN0qFEH`$%1*h}Yo9)(pdyi-PlNJ=l+7K?R5a=37V~"
    "><ES{(ks;MHqP4(^J}SUpkpr=g2XGrfr_D7QZ7Vt5e0e=r0K_!6fL7yUdbx8+R@jv+Ih~-?{C4csc)_JTL3d(R=d9}Nx^cR(izj4c3xlD8G&{IeF9P!3;6vE"
    "GDj%DY6r^?@?VC*o6VA+C1i>SKxTh9JRwRa0C$vtyHld2lKRs^mA44D=po5p^<06Cbx0qn08-Bkx!h9VM1738NoEQwyvzY}54GI!wj4G<_JKS`uLgbk7vDjx"
    "(IHZ-fANgC+W&~FD~|*O2d#Aah?CRwBTnkv@&VOHTK}0XdWkL9#vfcc{3+S1<q%mc+g>b4cM<?swpwg6BI_ACsF&DToW1T<o&xS2WFcXp;`{l8VKAI*s1Mui"
    "YW`R9D@s5+Ay-S!&|b>Si-|_N#hx|7WGTPFLrSN%Tfs{#a5nCeWHs`D2juFWQL=I+&6$9-1u9|(yz=3a8OJu!VJuF%kQgJEUZuylz5wF|5a2FBlZmZy8ReaK"
    "OUjp5EF%SgJIsJNovaj4UUh9BeJ%2qJh;m&hC~5O_uCD)0hA`N-3eHn(S$$Nn(S|>*`&5;F{-j?fg@G`wDq)UXXo#b?J|5WtKzMe2*&xgh#Z|Vf1qcI(5pq)"
    "LS-y|6x<RT&iFQ_<mV4KoxGx|C}>f{9^SSoUNP(lV0=_8wq*$Gajfm-W($7m0C31_$%m27`jtu)<BXwjQTlL1l|G1fWMlVBPhTNHi5VXZEJzhjl<0QbuAq|T"
    "j%VI0bS!67yOy8cp4nh$H#2Jd+F!7seox-|tr;y-0uMno<bJhm;9X@<yy3pQvxfHN9U&wEWEqzx5CsZAO^EbC(#et;*GzY{1&_Q^HMsQVPf@pdB>6?@?S9&@"
    "4`{_o+^z~BeGh78woP|+191Ry+1*$h9v-h$4w5UXq&s!__m}YO?QI<rOMu2M?ELyqdsyg!i6xLYDNSzb7XXedxD@1-Oel*_*|!F_Hg~VtBkJA-kWE=EHv0<*"
    "A7TKM$;lq!QKUPxc}7x2&>9DITNP*Pbo;#V3-rnrFJA|Ms;U6|G-^Q!idc|+Rjz>jO)a;CTge3p@UT?i50SNZV3hv~R!IQlAE+g9p~WJy0<dJ&rX3VPpYVs6"
    "#rzCe+YohcB&qD)s75xP%9cbWh>#;Po_Y=FT1>f_k`7T*BwalXe)0slHItL}j_k0&DW-ClPT9_x#oPP&U2E_lB`@c(r$9doRZP+!+56HH1X$8%5S{8o3;C^w"
    "U-%OQAOYO3udv|v>pkSe2!N1_Hl<-%p~x-B*l$#*$}dP=LvxBM$Ra^AL2jm%mS+Qy=;~z%l70cWg#@rtK>9$SNDf~%*aS|NLe<NE0t7?b-tM>F2MS8JB;ea`"
    "?`Io=dM7%6_FGCH?RIdsK={HvG+821`NlfIjrWj+BOn~!Xt6kg0I*A_#Tbb0r#Wxe!U?ylOmlDq3E&DO_KZ1QXFwa8w8><Ov}yP8m;a>pa~43>7yy`?)PfQn"
    "ISC{>E4qpUAUm=E=y_HOU>Q~myoi-TL?2urHJdc`q9zAf6a^Hg>6tTq)dax8xM+9997J_}-w2o$pt8m3gP+20b-9Fy@BP^Xz)Pc?zTr;l0Qe>a_@B5BcPy%u"
    "ChV}JGqi4URP;4n*&#a%mfb5za>u)1$kT?MB2QAn_*Mq{y8tQ<34pd!+TuqaHd4*v%w3zs{lShQCox)v1gjb4Z8C-f5t;{0t$VHU+rHK)F|i&nNxFNb(4Z`$"
    "kc3pJ;1-p&u6mYweL60>Z~R@lBySY}Vr;MU>F&}1P&g4la`e)te{%@1Cz3vk6Z<qaYyx|ZoTqpIAW4ceeSn_e336YuUtl0CMv4{%Ru8P8h{V=du$Tg1d7w=f"
    "TlH05?O%m?mf(akszG_hUO0GM!<`~PzGu}J#6}?BM47JGkwvFH5je;<z3%}nkhFYUhi}clW5cQWy5A>wrG~HobHXb?3ha1Jxw!ljwAtMHm3fo(E4GK)gk52w"
    "2}wc$Sk(DXe8o8C&1cAbb;q*x#yX_QBnq*By>Z<1){yLOLU%&@7>kgCP1G6tEa}|tbGt3Lykjepn5DnDwji_WE()ZLUdU5#9)RJ6sl5xbhx?_edwxWd|Ga<&"
    "J4ylGW0~>3!yy{GE_h`Hc;Uj;a_5;P-<@ZS6<#8bdQq{2J$R7Pn8gHe8a<@tAAn}MA7U)VThF|mtrJRlulE7~A^-t?7SwV>|C*Eeh$Y<D7<3B#OBJ3g0aO*Z"
    "GF&Kt8=uw*uT=AHolvXfzEhb*CW7GB3*jF|hQoE?ZQpz&juDKSA&xDd@o-dvojGvDHCKkkHI=<T<B?kR0_kxIY!5C?9%N0g3v~sf_*0C%s6Q^?GtNYLu|Pl4"
    "#;D--5+n+E3!PWDyW?eachE2NogE{;hZAp}`jT1-w-?Nn3T(IQpT5cEy1KGNe04=JN>C{=F7Q!zr&$8Xj~IZH`F@^7F@hQWmenmOr5a@qWm5I$;K`PqvK)m_"
    "KyL;jNVoXKN}WcT?zQBKnvumX6rH-w2Rht(GrvE<-sgTP@-970v9(tK1p@)6cWjyjBQIHvpn*P2@5cc^_--|^?LK535f+zMA1Un3w3~*UZJPNf%`|kVg6Euz"
    ">_Y)uC)j*pS*P;KN3Y^A>q#ten>BVhrVxn51}Fh=u*hExXP^N1Nd1|~0~W!Y`w>2Y>v`zglp%n5JIn8|gFs~7o7u%wdmu`<9}CdCQ+fF%{N97$denNGP7-hB"
    "_69)ESvwffj5gWIM~?*?m-NYf-cKduD(FdU7jGSs(aC%4ncONH9nyZpzI@SbDP8CTWpq^sbuId!y>i)`u!*|AjOYynMtbs}l6+|NI1lu|((~U(>)S~N!VCIA"
    "<{7g~?ec7x3Z-dr(op+fPbeQ4P>%JeKVxlj;FN!+|G~dPH>9Wh-<4pOiY=<XmGvrWF6GlPZdmP&p5esr77GCV>W2K18UIzk$A?}_hrbv3qy)fOQM6eygXLu%"
    "$)*C7^*;H9JUWfPADilyK_Sijow;o?SY6k!+^+)wKCKAB=Z1(K1hP>@@vH#zxN4IHcVw_)Ize`dG*$sxRq5<qC(A<$VBeS`V^xnuQnFZ<(IFp2T5SIEu|Yl="
    "xme|ZNPUocfe4AT`u2PIsYmKA<YJ5{O`fqHu%<Z<M{0*01?mc~UB`5w7O;C~Pd={gJIiX+R7d`K^|t)8MA)VL^ScMii;Wv$o9CnoQ+>$An>pBnw>k5p4s+(p"
    "H#IgVLpo{cb}jFBOgm&en!PYtLlc8y&7K#lxlb|f-J~ai*UcX3f#i^uBdshgkp8<o=1s*9AU#Y4ARBd3m`8$+jl-|DHOtS#XLBD_8-CMv3fmzP7=mk)KU{u}"
    "!b$;*dgtf<49krC|6~Z{{{S3!3gCRGJh}C6SfGX^0Q8Xp;G)#d2>ex^BHj0VME8(~k4Qmz#m=h)0W$=YC=;$W#fJm?zu1jkLW)|3RJKkhJX$sCrpM~%WQOVZ"
    "8*XEz4{`(KSgMI9GpL>Sm0os-&IlZUaVczVsCPT8qpZUHDsbueRRG79^r47v`-(J9lCjF$pDzGbs<f{f^MYt+`zpU3RwMGEn8Y~(NH^$twy$)TiN$hFG5&|f"
    "Dg~Z9>51a^uv3Ym?K27kclHSA2ngG2bY>v<bR$1$X~lB2hB<1whx-|oiihBulvkWwb;iJKE_TbF4c|N1q051;DazlEL-?}(bCAm6<%)a!#oojUIiA@QWQB4P"
    "%g58Ec$y!CWbes@o`j_mSJ|M4EMF}K`%B(X%3u>^5dfdObR(_m>5B>5R_!2*Z47kYbQmOlVc`}}E*NX_L>clS-mm48BmFg-g9V8kVx(ZhZ-!O4zZsT+UDDpp"
    "hPBEEcdXAN(%!AgL0Nv~7{r_9?fp=t9fF6eGL+l|xTie<d=%0d3%pfXeP2+uU#TP4znwvq;x#hRsCMTs5gliStJC=loC(20Q~p3SAv_m8n7_2p2eGf#Y@o{V"
    "VMc;Eu^<t*!f1$Ej5|gEq|;p)S5X(Yg_yTJeYWKcR&Vq}ZXZ2MzZbw~Vf#p718KsFw0I!PdGQcjY}~jd+(lNVb!z{}-)sI)0fEWSXnr6bz2++H$Tu*OPt?zC"
    "&cft3JG3V})!#{E3W(B))fsMVaSCD+&E>POtagk4XuQ>`CW743&tlQI!i*DKyHw(lGuuL1n&@`BCAe~s&iJe4GVtx`r@R1!ma8o10r0*@vLpro2efuhY&C!m"
    "(E{lpO_eHz<K#<790)LE$u;-R?%&^qWcb@K*zEzZXfd#2lVzj?ATLhtREFBTcCsMHV6H}}QzUm_1Jouk;w5+7VI_Cmd`Xl2`hH<5|6n0$X{O2tHp41>8Ft{D"
    ")JjXN|1WRyPgWFMROs8ay0YOGkZz^{5T<G%u@C@?8TWWVov@6Skq+TbwPe$2&@*TU%*e;X{Zys}4E3=Oq+95*U>E&(^1wQf+y!ZS*3!RtWs;tNI4yqO92AKI"
    "Srf!!%n;fKiJFN+01oB#(fcj1b1!RwNGq4>K2oTy`v~DE0ZgX7E#R9K0DqBxeZ`{verDO27EV8Yz~c9?L91fJYkeFX{s+MB<Xb{WShp_+&r~Z3r62zz24*Dz"
    "EQx$;TC_Tj9jLtZ%eIlRl`Ys9<<)zA1ONes0vpn`$%?22;MUb9gsMBwvYo`KNMU)c$Uh4=9PrBL^aP;`3&#B{NCW501LG(UlPxT?q#H!%{6^1*5{X!j*a*z&"
    "F*udUzOWdPZ*(!D{On@HjP&M*`_uw}ewFr_A%SOvfle*ad03NKvH{R^YvdKRQDUTHvz2$@<$m}khmrJI<j~~(4%xJW|1FDR5CQOb2q3?IEKAnBhcA*XW^;(s"
    "DX=d#eA#ikD(ip5aAl8Rxq@b~DSo=+I#xCdaBE8+un~1<kRK4B>7BU&G6!UwLE@_bY+L+P8Ly#*{@r{Y4hOGgUJHDyO9yTocRz%SNkAB5Q}6*wUuONe*O~l4"
    "-k}0n<G|E_!YRBWNjzL(EXPVYW5aYydDg;|@?=FnyocSGZnZ{OTYj-%zLfWJRRZ$~=&`6NlVdLys5PP&_sMo=<$=<Z<feT35`DL8?w#7jZDwI1&3dAbZ41eG"
    "Ha9Se${j*^YUdXmtoOqtSbYMxHd<<*#fcXDSeq%t668GObZVD;)cZNVvj0L86Q$&E#Jj};7L#)w+{&K%{kDF$6+R{Kmb<Oq8372fFds<{K_%L`PNHP#18=~&"
    "PA2r;8DG0L8Rb?mERtKLG-Za8bVjk*xlSj*xeh;!9L0nLJz)u7qvd|v{97vciFW{0YX{ja1|sP|LXc7c1FxTMFwFY#;mz$L?E#b>Ttr^^Nye`BmP=^aM%kY%"
    "BVn{ba9GmitRk^lhq;>4XMxO|J@`EZU@?Zsru*ImJBB~A`=pxoj3`8b$&ZEc34>hKw7;}H+KR)4bxwQV8*F5P;*wbe0xXFlc#o6rL;zy1?{P@%2tdxTHdWaK"
    "8fzH}Sd=$j@hMK1z)>zBz>JwLxycIwf;HnFL@8th@S#WgyFnU{G<gGrU3v^TjeE-O;e22qy<cDO%31&cNNBmfgdLj;hNHlUkG09d0dB#e>b0zdQKox+(SK2)"
    "pI|H|@6Ie3;xUQI4#J|wbOM9qPE#LqQ3ps-9%A16!yiy4Xg*dk{3!m1gVb)d<YW(?XB1}916PnrBwA*m0IXN#L*b~ALl`fXEAK9pF%bDe@fP-jUTi3qAU)$c"
    "bJ1f;q;!Dl@<Dw{>IlMqE#5*#sCKYoN&Q1W{U(<IZtD-nvusA~gB@Jo)_&MVITKALzx3Qphi`4UVqi-J8ic>$4PM&4YEOaKQGKIdMW$kTq`U@yepK$BbtC%n"
    "H}_KkIv*->v!C$WI6rCT2J=5-s9e*(@o@bE%K3P0{m<J!7V-xpRxWVm+<x-%S^rYu^^`9WZQYScKFcH>T!$E_Fahodn*|=r*ox}0OQi=zDAsR&fosZYi{iX&"
    "`xH4Lem=dV_Xn@_2AN-dJ6f3-$(#q$Um@3Tcd4ypwA--or&uXpX86W$55K8JJ$AS@l$zg9H-tshQr$*ZHL%L!?Ek){6X21A5&GB3E<i2`^zr8hP5K&7k@Bq{"
    "gvzW#EUM&vhzK{eNl*L8pGL+X`=LRfQI#<>9Nv)p8MXd*65cubaMhK{%b3&UD3Z3wRUs|MED#p8KVi!6xt3A&Bioqh--0N1d*?md)6pHcy_FU{SwgSaF>VV8"
    "R`!c8_S{}|l`Kg^epUq*_P4Ur=c(+^)MJs7^z@6B9?D6==L+~K1h^HXLRGv6dwkA~z^Ix8Xqt3!!Mf3N1EZ_-B>mpG;XRdjEOrOyh9*iSC#=V`x8C-XTN3#!"
    "bNp(5<X6Z?fMP&Cbh+lq5sN9VuviknQd7%D4)SYA0ti6DyZ|?EQNL4N#b8#EXm;@fIjg~~gaAbF^G4?4$^=n7zng&{RV)Oz5~(*T6Sz1OSa3(aNw^5$OYw)_"
    "3~`?7*ih@u0Ldu15{rUK9}u1iptiYmwpr54Pq4ahPY0wiU<c%_4qm(lz&x3}>TLVn9cnIuLk`&*^3^fZ`zAZPH~<Iab6bleawBhTW5~lGY(eL;jo6L!#J#FL"
    "f8p*}_-C8e4~HOQDb|}KYOw{trz!wc8t!ULhre`2iA3%gtc@1LigV>`*pT}5H3KE`(}0Som-U|?z53Pf+mfT4kFu%rh)ruxEgs2o9V`36m!WQTcR9XA4w!Va"
    "`b4!Le4tG)f5nn=M}?Cg09HgU*W?sjuKA(Iv;S#X%KNdmwbA=x+3$xszl6u<V1QJp4of5+pWWoQ%s$u!1ep}G3m%_A2`R@$yOJwI!;e{br|$>36$#`bb?A6|"
    "jo$vsTP*DFr;N-~u;0(EKm8|nk#-jr-vpi9qdDT<9uf5xfDOJ{Y^Nq2D2Xb-YEq<$S&;&)rdw_UQa{Gi<hhfkAF$azV!f&-1U;@;EOA0RTLPXoC3zX#@hzXY"
    "mV3<Tg84B+Kg03~Ka(8->Z>tcy;nphbI5IWOMO%gX!$MDz{G;Y#dDiQ8OcO|qL}WSW#*>}qMXtMiCM8kTbn*h@}<v7Cv@hDoMb1}Q*K-=bxM729k<VdD%ehT"
    "H?Sj4B%Sf?DY#X`mctY~u#m<+DN-u{c{QCk>?_5>@1$!vtEYE&p~*{F?c9$Q($+t`L+?!<NoovlwiLho%>_66mD|bSBLhGNvCS3=ml_!X4^F3{`9GI$%#vZ}"
    "6FVk9WeH%79T-@HTSeA0?qTm9ZO=Y$xbJCnz@#7@ybUO>UP2R&)kAOt^nb{OG;d&EAWh&n69DI@Z*^_n%L6t|0$4mK;JDVH9=5}S3tnC0@DdRG*zy~s7O5hm"
    "^QodrxXD|)`Q6^9tOtyM&ql?|g*8N}A_4@`fhs`|d3^@o%`5Uhk<KJ<;l`0xRBnm|DpLaJX8C!=21=XkejqDtm9k9!w(oBm0D;jLgz>qzus^|y?!8weT}+uV"
    "(wZ_J2OhE5z<)0TAbnH-yh92=9h2!8)A4SEM_mB6Siug$P_L*u5D?Krz9Q*UEqe!m<v<5;)Rnve3Ta9RPlheaCh2{0r-ZbChl6{zuVa}(9gA3GGiF=0HUisj"
    "?1Wd=V+*itjAscDZgBw4VtI@C*nf54WA&Q0j_<+?JPm7EFEeB6;kv=x#A}Opl~EgbnKoI_oD2C2zB<hQFAi8TnrV}TSvuqK%e2AVsTO2q6$f+&hy|pzUjx!C"
    "od<q=siJ&PAUO|^=PCgAfmbR78FNwneuC{xEFeIVaRlWt$XRp`72o8!ynNRiqzTH%-|D(#PwXPUN2V^NGKvV{Y$nTk&kGl<!qOkX204Qze@F*++|U@U5nK2#"
    "F(^@co3pnyAEjNt>=;>vD*&FR@;BuxlON1ZPJUpMpnWXAFnCC_W-pmyL7Mcj@Q(m^*24G#uU=sY00)YfYa^9efLk6AKp6aq%A8_hd`Oz?6a8`#qtgBQj>-gC"
    "C5QFA{(;LQ-uiLeqJ7jHDzLK&U{#3#t1Z;CnafPiW{KuvL6lwkutHcm7oO2XcBp1QggnlxQ4lY4sJjb$X}m(8Cv5+)V4y)+U9YfYd0Q_Hpq5D<7O!?jXR^<T"
    "#j3^hJVw;4ovn;tEF|46EEzz$+I&;9`0gniT&Dn3)2$saPl!ckN_TwnA(3&7gN;S)DBQZn`J=be;F^&p#+IbB4H|md?jbrVW2!+mIL=4pNiK|JxZtr_RDbP|"
    "2khybkpX}*gO^`2RZc9pV+B|`tenu#W&n_wD2qim`OGHUEei+|7fOlFsU{@dkk=(!0*p2Sn3g2{L5wVCfR<gN%AZv}#U`!$G5@cP9cjEl`j6}>S&v>{Ld!-h"
    "@b|0b2eO_o;R*GQOVA_=@F$<_yiDo0kAk^}w>$r&CDIiY^w;bO-faW&G$PYMrYV+acXy=y&wjA}K1yxV<v&zJ)sn?gq@0PJ!`hmCifNW~Yd6H1cP!)9lQ$_H"
    "F6YORIr{;ZlC~mGM=X}8>z@wT-*|;I2e0`XGGWC6Z<AY|Q7lX>^$k0tepCRQe1$ZtvI=Rp*ut5O1tH@mf7mmdm#qehKJ5%E0<84q<fkLgfPKG!GXfW%NCky="
    "hq(qD$6eS>pZP^)gS5iaEPo>^GlCuEBc+c#D*ybUf6?7t+Bo36;t>!FBgf7wykOc#rAycfhokHz$fvve^m;aH$RZE7Zs&vnTskwhxBEnrpFgXSpz+q?-?wqF"
    "xYxrG<H`JTV=Px`;(-vEbZ-Mx;P_4kV}e+?R(3L|1=1#a<P}We*_mU~R14#>11tli30`%zfW~OJkK8Ep$a^w(%RCQ>ByR)CC(8BgcphA*UWS3-;pVrkD(0gI"
    "S@OHH!S5r_DOUVSf|D*Iyeb$mZ*8^Zy8xyyoLjD~p51<lJr8qzpi!k+{bZ;>z$Okridg~1JS70@3jY}#D`Rs0Kd*VOwa-v}@p@~-1A^s2-C^^wzeb7L0U;v)"
    ">*#->%C3SHo&a#!czL7^IoMhYAnk5@?bhJYb0X)R6J@MA=0o`=rpwF;-`Y&AZm;1lR^#x8-HutF4fViVn~bKQ2n4O^f{XrYRLFNJlm2k~iCIi6kcg0FE)xNz"
    "X~jMqUALd$w9-DHvJwj%CEb{xwF&O&K+@%@gZV<nKf2wg4u`<ZEMnb4V)PUCU;-lF>yy_<f#?%7)zvb9x9$n#!~&w+sVBt$v@-~m4pCK-Sd1%Per~Te2VkY8"
    "Y>+@ZB2B&1zcjsqL+BgpVC`)Q7uv~g9RRx9Wp#*eytZ;v9kwF>VrT=wDCuP_2j}#7KOn^V$nv03lDxsEN8Y$c^N2tUeYBv8+=xlmUhS1hb|dQh2%yA5?pJob"
    "w)eVtR{kX*`1z&9l4lj15GuTc&)EN6+|`v98;KNv{aX$<t_Z|o<dxZK=@hx3(kXb>y?n>b*^Z)^l?5o};a*})lay7d9VqK6F45v=>dGk*(JKHP$qJxj_`-0F"
    "TYQ3dN-X$_f<m0%PZGPdN3Zw&_W;OS#<-k3d7h*LCU=J%`0mFI6>MT51N_fpuvikH6i?1$TRq?Eu;ot0F33QiV2){E<`$~}c&^k^rUmIs2KxW}A!8Apw?HAG"
    "$JtP<0QFsRf?U^=dE2g6-a_C*?dQ{<2s5g(Ro~JEF1$rlQhQpkN5My4COsL1@fMyDyVy7`gMu;ocYLv_d+_^R-(2&0#qfI1TYMnWv%51<R{J(DBbtF{Am!8x"
    "mKoTbGTQmzu$%GqU?nCu7nNqUju$EWXL9z5r3E*NLn?uoQb4K;{)nn(2ib4_>4%G>(~tKFb>bfm<0meywaI?};Aa)w(%3u-cF#-7n*6K~%~B%@Wq(%qa<nPe"
    "&~)UeCue8N@Ng$(^4fg#11u7MEfkSHQE2CP%b)mntF!<38SZ<3(gcZ&062FPSS5__JR+kgY&)J6*a+a0G-<-iqfMq2Af4fsk|unsVa-udP>i&K2Xz97YPNT7"
    "-SP-8Gw?hL2<LHsa==|7KM++5;y>;c+RHf%T4LckvGRtEo4bDxhgY|}1#z-Q+DwB^f$i56SOJv)l#8fk0bgp574k0?jw`1RQ0*d>{9hmh`m{HeN2d?@yzpsG"
    "qlx#q@n@<e#g(V(|NP(o_x}M`q#BF"
)


def _load_hsk_word_data():
    payload = zlib.decompress(base64.b85decode(_HSK_WORD_DATA_B85.encode("ascii")))
    levels_list = json.loads(payload.decode("utf-8"))

    levels = {}
    word_to_level = {}
    for level in HSK_WORD_LEVEL_ORDER:
        words = set(levels_list[level])
        levels[level] = words
        for word in words:
            word_to_level[word] = level

    return levels, word_to_level


HSK_WORD_LEVELS, HSK_WORD_TO_LEVEL = _load_hsk_word_data()


def hsk_word_coverage(unique_words):
    """
    Given a set/list of unique segmented words, return HSK vocabulary coverage
    using the embedded New HSK vocabulary data.
    """
    unique = set(unique_words)
    total = len(unique)
    if total == 0:
        empty_levels = {lvl: {"count": 0, "pct": 0.0, "words": set()} for lvl in HSK_WORD_LEVEL_ORDER}
        empty_cum = {lvl: {"count": 0, "pct": 0.0} for lvl in HSK_WORD_LEVEL_ORDER}
        return {
            "per_level": empty_levels,
            "cumulative": empty_cum,
            "not_in_hsk": set(),
            "not_in_hsk_count": 0,
            "not_in_hsk_pct": 0.0,
        }

    per_level = {}
    cumulative = {}
    covered_so_far = set()

    for level in HSK_WORD_LEVEL_ORDER:
        words_in_level = unique & HSK_WORD_LEVELS[level]
        per_level[level] = {
            "count": len(words_in_level),
            "pct": len(words_in_level) / total * 100,
            "words": words_in_level,
        }
        covered_so_far |= words_in_level
        cumulative[level] = {
            "count": len(covered_so_far),
            "pct": len(covered_so_far) / total * 100,
        }

    not_in_hsk = unique - covered_so_far
    return {
        "per_level": per_level,
        "cumulative": cumulative,
        "not_in_hsk": not_in_hsk,
        "not_in_hsk_count": len(not_in_hsk),
        "not_in_hsk_pct": len(not_in_hsk) / total * 100,
    }
