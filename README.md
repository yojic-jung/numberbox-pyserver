# NUMBERBOX-pyserver
> 위 프로젝트는 N명의수학 서비스의 소켓서버를 구현한 프로젝트로 한글문서 변환을 처리합니다.  
> N명의수학은 초중고 수학교육과정에 맞춤화된 수학컨텐츠 제작 및 공유 플랫폼입니다.  
> 개발기간 : **22.11 ~ 23.1**

<br/>

## 시스템 구성(인프라)
<img src="https://github.com/yojic-jung/back/assets/45252387/9d44771a-2fac-4bbb-8af5-8a678ed04500" width="500" >
<br/><br/><br/>

## 실행가이드
> Socket 프로젝트
1. python(v3.9.11) 설치  
<br/>

2. 깃을 통해 프로젝트 다운  
```
git clone https://github.com/yojic-jung/numberbox-pyserver.git
```
3. 프로젝트 루트경로로 이동  
```
cd numberbox-pyserver
```
4. 모듈 설치  
```
pip install pywin32
pip install ApScheduler
```
5. 실행  
```
python main.py
```

<br/>

## 소스파일
* [./main.py](https://github.com/yojic-jung/numberbox-pyserver/blob/master/main.py) : 소켓 서버 구현
* [./customHwp.py](https://github.com/yojic-jung/numberbox-pyserver/blob/master/customHwp.py) : *.hwp문서 생성 및 변환 함수
* [./commonUtil.py](https://github.com/yojic-jung/numberbox-pyserver/blob/master/commonUtil.py) :  공통함수
