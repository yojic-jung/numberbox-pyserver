# NUMBERBOX-pyserver
> N명의수학은 초중고 수학교육과정에 맞춤화된 수학컨텐츠 제작 및 공유 플랫폼입니다.
> 위 프로젝트는 N명의수학 서비스의 소켓서버를 구현한 프로젝트로 한글문서 변환을 주로 처리합니다.

<br/><br/>

## 개발기간
> **22.02 ~ 22.11(개발) : 8개월 간 웹서비스 구축 및 수학컨텐츠 제작**<br/> **22.11 ~ 23.07(운영) : 유지보수 및 기능 업데이트**
<br/>

## 시스템 구성(인프라)
<img src="https://github.com/yojic-jung/back/assets/45252387/9d44771a-2fac-4bbb-8af5-8a678ed04500" width="500" >
<br/><br/><br/>

## 실행가이드
> Socket 프로젝트
1. python(v3.9.11) 설치
2. npm(v8.19.2) 설치

3. 깃을 통해 프로젝트 다운
```
git clone https://github.com/yojic-jung/numberbox-pyserver.git
```
4. 프로젝트 루트경로로 이동
```
cd numberbox-pyserver
```
5. 실행
```
./main.py
```
<br/><br/>

## Environments
<img src="https://img.shields.io/badge/amazonec2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white"><img src="https://img.shields.io/badge/windows-0078D4?style=for-the-badge&logo=windows&logoColor=white"><img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">

<br/><br/>

## 라이브러리
* react-geogebra
* react-helmet-async  
* react-router-dom  
* react-sortablejs
<br/><br/>

## 핵심기능 구현로직

* [수식에디터 기능구현](https://github.com/yojic-jung/NUMBERBOX-web/blob/master/src/js/contents/register/contents_reg.js#L1943) : 수식에디터 keyDown이벤트에 적용된 소스로 에디터 기능 구현, 수식 편집 규칙, 버그제어 로직이 구현된 함수
  
* [수식문법 변환](https://github.com/yojic-jung/NUMBERBOX-web/blob/master/src/js/convertGrammer/nbToTexConvert_cvt.js) : web수식 ⇄ tex수식 양방향 변환 규칙 정의된 함수 파일(해당 로직을 통해 web ⇄ hwp문서 변환가능)
* [수식에디터 UI 컴포넌트](https://github.com/yojic-jung/NUMBERBOX-web/blob/master/src/web/contents/register/FormulaEditor.js#L810) : 아래 태그에 걸려있는 이벤트 함수들이 주요 에디터 기능을 구현하는데 사용되는 함수  
```
<div id="contentsFormulaEditor" className="contentsFormulaEditor contentEditClass onlyEdit" contentEditable="true"  spellCheck={false} placeholder="문제를 입력해주세요..." onKeyDown={(event) => {reg_preventKeyEvent(event, isMyContents);copyPreventEv(event)}} onKeyUp={(event) => {formulaConvert(event, shortCutKeyList);reg_dressSelectionBackColor();reg_tbCellKeyUp(event);reg_nbComplie(event);nb_base64ImgRegisterToS3(event);reg_convertFigureTagRemove("contentsFormulaEditor");}} onClick={()=>{reg_dressYellowBox()}} onMouseDown={()=>{reg_selectCheck()}} onPaste={(event)=>{reg_tbPasteInPastePrevent(event)}} onCopy={(event)=>{reg_imageCopy(event, true)}} onCut={(event)=>{reg_imageCopy(event, false)}}></div>
```

<br/><br/>

## 패키지 구조
```bash
.
├── package-lock.json
├── package.json
├── public
│   ├── index.html
│   ├── manifest.json
│   ├── robots.txt
│   ├── rss.xml
│   └── sitemap.xml
└── src
    ├── App.css
    ├── App.js
    ├── App.test.js
    ├── css
    ├── font
    ├── img
    ├── index.css
    ├── index.js
    ├── js            // js 폴더
    │   ├── common                //공통 js함수 폴더
    │   │   ├── common_nb.js
    │   │   ├── makePdf.js
    │   │   └── useScript.js
    │   ├── contents              
    │   │   └── register
    │   │       └── contents_reg.js        // 수식에디터 기능 및 버그제어 js함수
    │   └── convertGrammer        
    │       └── nbToTexConvert_cvt.js      // web수식과 hwp수식 변환 js함수
    ├── logo.svg
    ├── reportWebVitals.js
    ├── setupTests.js
    └── web            //컴포넌트(각 컴포넌트에 실행되는 js포함)
        ├── admin                      //관리자 
        │   ├── AdminSvcCenter.js
        │   ├── MathTypeCategory.js
        │   └── MembersStatistic.js
        ├── common                    //공통 컴포넌트
        │   ├── BottomMenuBar.js
        │   ├── CustomBarChart.js
        │   ├── CustomPieChart.js
        │   ├── CustomPrivateRoute.js
        │   ├── CustomSelBoxDown.js
        │   ├── CustomSelBoxUp.js
        │   ├── CustomSelectBox.js
        │   ├── CustomTypeSelBox.js
        │   ├── CustomUnitSelBox.js
        │   ├── DetailedContentsWrap.js
        │   ├── EmptyList.js
        │   ├── ErrorReportForMathCon.js
        │   ├── FollowListBox.js
        │   ├── LicenseUi.js
        │   ├── LicenseUi2.js
        │   ├── MultiRangeSlider.js
        │   ├── MyContentsSearchFilter.js
        │   ├── MyPageList.js
        │   ├── PageNumBtn.js
        │   ├── ProfileComponent.js
        │   ├── ResourceMenuBar.js
        │   ├── RoundButtonList.js
        │   ├── ServiceCenter.js
        │   ├── StatisticTable.js
        │   ├── TabButton.js
        │   ├── TabTable.js
        │   ├── ToggleButton.js
        │   ├── TopMenuBar.js
        │   ├── TypeSelBox.js
        │   ├── UnitSelBox.js
        │   └── UnitTypeCombo.js
        ├── contents
        │   ├── list                      //문제검색 및 공유, 나의 제작문제, 저장소 문제, 프로필
        │   │   ├── ContentsList.js
        │   │   ├── IpsiWorkContentsList.js
        │   │   ├── MyAccountDrop.js
        │   │   ├── MyContentsList.js
        │   │   ├── MyMathDocs.js
        │   │   ├── MyPageWrap.js
        │   │   ├── MyProfile.js
        │   │   ├── MyRepository.js
        │   │   ├── MyResource.js
        │   │   ├── UserProfileWrap.js
        │   │   └── WorkContentsList.js
        │   ├── mathDocs                //학습지 제작 및 결과 템플릿
        │   │   ├── MathDocsMaker.js 
        │   │   └── MathDocsPaperA.js
        │   └── register                //수식에디터 컴포넌트
        │       ├── EditTableInnerUi.js
        │       ├── FormulaEditor.js
        │       ├── FormulaEditorMulti.js
        │       ├── FormulaEditorUnitForMulti.js
        │       ├── FormulaShortCutKey.js
        │       ├── NbWebEditor.js
        │       ├── RegisterContents.js
        │       ├── RegisterContentsForImg.js
        │       ├── RegisterContentsInfo.js
        │       └── RegisterContentsMulti.js
        ├── fileConvert
        │   └── HwpToHtml.js          //파일변환 컴포넌트
        ├── mathResource              //도형 및 이미지 제작 및 공유 컴포넌트
        │   ├── GraphMake.js
        │   ├── RegisterResource.js
        │   ├── RegisterResourceInp.js
        │   └── ShareResource.js
        └── page                     // 기타 컴포넌트
            ├── AccessDenied.js
            ├── AdminMenuBar.js
            ├── EmailPassFind.js
            ├── Login.js
            ├── Main.js
            ├── NaverLoginSuccess.js
            ├── NotFound.js
            ├── PrivacyPolicy.js
            ├── ServicePolicy.js
            └── SignUp.js


```
