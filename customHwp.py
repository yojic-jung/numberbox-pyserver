# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 17:49:17 2022

@author: 정요직
"""

import win32com.client as win32
import os
import pythoncom
import base64
from os import remove
from datetime import datetime
import random
import shutil
import json
import time

def makeHwp(pagePadding, align, fontSize, charSpacing):
    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject", pythoncom.CoInitialize())
    hwp.XHwpWindows.Item(0).Visible = False
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckModule")
    # 페이지 여백 설정
    if pagePadding == "좁게":
        hwp.HAction.GetDefault("PageSetup", hwp.HParameterSet.HSecDef.HSet)
        hwp.HParameterSet.HSecDef.PageDef.Landscape = 2
        hwp.HParameterSet.HSecDef.PageDef.TopMargin = hwp.MiliToHwpUnit(15.0)
        hwp.HParameterSet.HSecDef.PageDef.BottomMargin = hwp.MiliToHwpUnit(15.0)
        hwp.HParameterSet.HSecDef.PageDef.LeftMargin = hwp.MiliToHwpUnit(15.0)
        hwp.HParameterSet.HSecDef.PageDef.RightMargin = hwp.MiliToHwpUnit(15.0)
        hwp.HParameterSet.HSecDef.PageDef.HeaderLen = hwp.MiliToHwpUnit(10.0)
        hwp.HParameterSet.HSecDef.PageDef.FooterLen = hwp.MiliToHwpUnit(10.0)
        hwp.HAction.Execute("PageSetup", hwp.HParameterSet.HSecDef.HSet)

    if align == "alignLeft":
        hwp.Run("ParagraphShapeAlignLeft")  # 최초 왼쪽 정렬 속성 주고 시작(default가 양쪽 정렬이기에 자간간격이 벌어지는 현상 나타남)

    while charSpacing != 0 and charSpacing < 0:
        hwp.Run("CharShapeSpacingDecrease")
        charSpacing = charSpacing + 1

    # 줄나눔 기준
    hwp.HAction.GetDefault("ParagraphShape", hwp.HParameterSet.HParaShape.HSet)
    hwp.HParameterSet.HParaShape.BreakNonLatinWord = True  # 글자 단위로 줄 나눔
    hwp.HAction.Execute("ParagraphShape", hwp.HParameterSet.HParaShape.HSet)

    setFont(hwp, fontSize);  # 폰트 크기 9pt로 설정

    return hwp


# 다단 설정
def setMultiColLayout(hwp, cnt, line):
    hwp.HAction.GetDefault("MultiColumn", hwp.HParameterSet.HColDef.HSet)
    hwp.HParameterSet.HColDef.type = 0
    hwp.HParameterSet.HColDef.Count = cnt
    hwp.HParameterSet.HColDef.SameSize = 1
    hwp.HParameterSet.HColDef.SameGap = hwp.MiliToHwpUnit(5.0)
    hwp.HParameterSet.HColDef.Layout = 0
    if (line == "SOLID"):
        hwp.HParameterSet.HColDef.LineType = 1
        hwp.HParameterSet.HColDef.LineWidth = hwp.MiliToHwpUnit(2.0)
        hwp.HParameterSet.HColDef.HSet.SetItem("ApplyTo", 6)
    hwp.HAction.Execute("MultiColumn", hwp.HParameterSet.HColDef.HSet)


# 텍스트 삽입
def insertHwpText(hwp, jsonObjForHwp):
    hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
    hwp.HParameterSet.HInsertText.Text = jsonObjForHwp["contents"]
    hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)


# 밑줄 효과 실행
def executeUnderLine(hwp):
    hwp.Run("CharShapeUnderline")


# 글자 크기 셋
def setFont(hwp, fontSize):
    char_shape = hwp.CharShape
    char_shape.SetItem("UseFontSpace", 0)
    char_shape.SetItem("Height", fontSize)
    hwp.CharShape = char_shape


def takeHwpPosInfo(hwp, idx):
    # KeyIndicator 반환값
    # 0 : ??
    # 1 : 총 구역
    # 2 : 현재 구역
    # 3 : 현재 쪽
    # 4 : 현재 단
    # 5 : 현재 줄
    # 6 : 현재 칸
    # 7 : 삽입/수정모드
    # 8 : 현재 위치 컨트롤
    return hwp.KeyIndicator()[idx]


# 이미지 삽입
def insertHwpImg(hwp, jsonObjForHwp):
    png_recovered = base64.b64decode(jsonObjForHwp["contents"])
    # 시스템시간_난수 파일명 생성
    nowDate = str(datetime.now()).replace("-", "").replace(" ", "_").replace(":", "").replace(".", "_")
    randNum = str(int(random.random() * 10 ** 9))
    imgFileName = nowDate + "_" + randNum + "_image.png"
    imgFile = open(imgFileName, 'wb')
    imgFile.write(png_recovered)
    imgFile.close()  # 이미지 생성

    # 이미지 크기 px to mm
    # 이미지 셋팅시 추가되는 좌우 여백 3mm(12px)만큼 크기 제거
    imgSizeRatio = int(jsonObjForHwp["imgHeight"]) / int(jsonObjForHwp["imgWidth"])
    imgWidth = int(jsonObjForHwp["imgWidth"] - 12) * 0.264
    imgHeight = int(jsonObjForHwp["imgHeight"] - 12 * imgSizeRatio) * 0.264

    # 현재 캐럿이 현재 줄의 첫번째 칸이 아니면 한 줄 뛰고 이미지 삽입
    currentCell = takeHwpPosInfo(hwp, 6)
    if (currentCell != 0):
        hwp.Run("BreakPara")

    # 이미지 추가
    # 파라미터(파일 경로, 문서 내 포함 여부, 사이즈 크기 지정 옵션, 이미지 반전 옵션, 워터마크 효과 유무, 그림효과, 가로, 세로)
    hwp.InsertPicture(os.getcwd() + "\\" + imgFileName, True, 1, False, False, 0, imgWidth, imgHeight)
    remove(os.getcwd() + "\\" + imgFileName)  # 이미지 삭제

    hwp.FindCtrl()  # 캐럿 앞(또는 뒤) 객체 선택
    hwp.HAction.GetDefault("ShapeObjDialog", hwp.HParameterSet.HShapeObject.HSet)
    if (jsonObjForHwp["float"] == "left"):
        hwp.HParameterSet.HShapeObject.HSet.SetItem("TreatAsChar", False)  # 글자처럼 취급하지 않음
        hwp.HParameterSet.HShapeObject.HSet.SetItem("TextWrap", 0)  # 어울림
        hwp.HParameterSet.HShapeObject.HSet.SetItem("HorzAlign", 0)  # 가로 왼쪽 정렬
    elif (jsonObjForHwp["float"] == "right"):
        hwp.HParameterSet.HShapeObject.HSet.SetItem("TreatAsChar", False)  # 글자처럼 취급하지 않음
        hwp.HParameterSet.HShapeObject.HSet.SetItem("TextWrap", 0)  # 어울림
        hwp.HParameterSet.HShapeObject.HSet.SetItem("HorzAlign", 2)  # 가로 오른쪽 정렬
    elif (jsonObjForHwp["float"] == "asBlockCenter"):
        hwp.HParameterSet.HShapeObject.HSet.SetItem("TreatAsChar", False)  # 글자처럼 취급하지 않음
        hwp.HParameterSet.HShapeObject.HSet.SetItem("TextWrap", 1)  # 자리차지
        hwp.HParameterSet.HShapeObject.HSet.SetItem("HorzAlign", 1)  # 가로 가운데 정렬
    elif (jsonObjForHwp["float"] == "asBlockRight"):
        hwp.HParameterSet.HShapeObject.HSet.SetItem("TreatAsChar", False)  # 글자처럼 취급하지 않음
        hwp.HParameterSet.HShapeObject.HSet.SetItem("TextWrap", 1)  # 자리차지
        hwp.HParameterSet.HShapeObject.HSet.SetItem("HorzAlign", 2)  # 가로 오른쪽 정렬
    elif (jsonObjForHwp["float"] == "asChar" or jsonObjForHwp["float"] == "asCharNoBreakPara"):
        hwp.HParameterSet.HShapeObject.HSet.SetItem("TreatAsChar", True)  # 글자처럼 취급

    hwp.HParameterSet.HShapeObject.HSet.SetItem("OutsideMarginLeft", hwp.MiliToHwpUnit(1.5))  # 이미지 왼쪽 바깥쪽 여백
    hwp.HParameterSet.HShapeObject.HSet.SetItem("OutsideMarginRight", hwp.MiliToHwpUnit(1.5))  # 이미지 오른쪽 바깥쪽 여백
    hwp.HAction.Execute("ShapeObjDialog", hwp.HParameterSet.HShapeObject.HSet)
    hwp.Run("Cancel")
    hwp.Run("MoveRight")

    if (jsonObjForHwp["float"] == "asBlockCenter") or (jsonObjForHwp["float"] == "asBlockRight") or (
            jsonObjForHwp["float"] == "asChar"):
        hwp.Run("BreakPara")


# 수식 삽입
def insertHwpEquation(hwp, jsonObjForHwp):
    hwp.HAction.GetDefault("EquationCreate", hwp.HParameterSet.HEqEdit.HSet)
    hwp.HParameterSet.HEqEdit.Version = "Equation Version 60"
    hwp.HParameterSet.HEqEdit.EqFontName = "HancomEQN"
    hwp.HParameterSet.HEqEdit.string = jsonObjForHwp["contents"]
    hwp.HParameterSet.HEqEdit.BaseUnit = hwp.PointToHwpUnit(9.0)  # 수식 폰트 크기 : 30
    hwp.HParameterSet.HEqEdit.TreatAsChar = 1  # 글자처럼 취급
    hwp.HAction.Execute("EquationCreate", hwp.HParameterSet.HEqEdit.HSet)  # 폰트이상함

    # 수식 한번 더 선택하여 속성 재등록 후 실행(폰트 제대로 등록 안되는 오류 해결)
    """
    hwp.FindCtrl()  # 다시 선택
    hwp.HAction.GetDefault("EquationPropertyDialog", hwp.HParameterSet.HShapeObject.HSet)
    hwp.HParameterSet.HShapeObject.HSet.SetItem("ShapeType", 3)
    hwp.HParameterSet.HShapeObject.Version = "Equation Version 60"
    hwp.HParameterSet.HShapeObject.EqFontName = "HancomEQN"
    hwp.HParameterSet.HShapeObject.HSet.SetItem("ApplyTo", 0)
    hwp.HParameterSet.HShapeObject.HSet.SetItem("TreatAsChar", 1)
    hwp.Run("Cancel")  # 폰트 예뻐짐
    hwp.Run("MoveRight")  # 커서 오른쪽으로 이동, 다음 수식 삽입 준비
    """


# 표 생성 함수
def insertHwpTable(hwp, jsonObjForHwp):
    hwp.HAction.GetDefault("TableCreate", hwp.HParameterSet.HTableCreation.HSet)  # 표 생성 시작
    hwp.HParameterSet.HTableCreation.Rows = jsonObjForHwp["rowCnt"]  # 행 갯수
    hwp.HParameterSet.HTableCreation.Cols = jsonObjForHwp["colCnt"]  # 열 갯수
    hwp.HParameterSet.HTableCreation.WidthType = 2  # 너비 지정(0:단에맞춤, 1:문단에맞춤, 2:임의값)
    hwp.HParameterSet.HTableCreation.HeightType = 0  # 높이 지정(0:자동, 1:임의값)

    tbWidth = 0  # 표 전체 너비
    for colWidth in jsonObjForHwp["colWidthList"]:
        tbWidth += colWidth

    # 표 셀 너비 비율에 따라 셋팅
    tbColRatioList = []
    for colWidth in jsonObjForHwp["colWidthList"]:
        tbColRatioList.append(82 * colWidth / tbWidth - 1)

    hwp.HParameterSet.HTableCreation.WidthValue = hwp.MiliToHwpUnit(
        82.0 - 1 * jsonObjForHwp["colCnt"])  # 표 너비, 셀 여백 빼주기

    # hwp.HParameterSet.HTableCreation.HeightValue = hwp.MiliToHwpUnit(13)  # 표 높이
    # 열 생성
    hwp.HParameterSet.HTableCreation.CreateItemArray("ColWidth", jsonObjForHwp["colCnt"])
    for i in range(len(jsonObjForHwp["colWidthList"])):
        if jsonObjForHwp["contentsDetailType"] == "table":
            hwp.HParameterSet.HTableCreation.ColWidth.SetItem(i, hwp.MiliToHwpUnit(tbColRatioList[i]))  # 열 너비 셋팅
        else:
            hwp.HParameterSet.HTableCreation.ColWidth.SetItem(i, hwp.MiliToHwpUnit(
                int(jsonObjForHwp["colWidthList"][i] * 0.264)))  # 열 너비 셋팅

    # 행 생성
    # hwp.HParameterSet.HTableCreation.CreateItemArray("RowHeight", jsonObjForHwp["rowCnt"])  # 행 생성
    # for i in range(jsonObjForHwp["rowCnt"]):
    # hwp.HParameterSet.HTableCreation.RowHeight.SetItem(i, hwp.MiliToHwpUnit(6.0))  # 1행

    hwp.HParameterSet.HTableCreation.TableProperties.Width = hwp.MiliToHwpUnit(82.0)  # 표 너비

    if jsonObjForHwp["contentsDetailType"] == "table":
        hwp.HParameterSet.HTableCreation.TableProperties.CellMarginTop = hwp.MiliToHwpUnit(1.3)  # 표 안 셀 위쪽 여백
        hwp.HParameterSet.HTableCreation.TableProperties.CellMarginBottom = hwp.MiliToHwpUnit(1.3)  # 표 안 셀 아래쪽 여백
        hwp.HParameterSet.HTableCreation.TableProperties.CellMarginLeft = hwp.MiliToHwpUnit(0.5)  # 표 안 셀 왼쪽 여백
        hwp.HParameterSet.HTableCreation.TableProperties.CellMarginRight = hwp.MiliToHwpUnit(0.5)  # 표 안 셀 오른쪽 여백
    else:
        hwp.HParameterSet.HTableCreation.TableProperties.CellMarginTop = hwp.MiliToHwpUnit(0.5)  # 표 안 셀 위쪽 여백
        hwp.HParameterSet.HTableCreation.TableProperties.CellMarginBottom = hwp.MiliToHwpUnit(0.5)  # 표 안 셀 아래쪽 여백
        hwp.HParameterSet.HTableCreation.TableProperties.CellMarginLeft = hwp.MiliToHwpUnit(1.0)  # 표 안 셀 왼쪽 여백
        hwp.HParameterSet.HTableCreation.TableProperties.CellMarginRight = hwp.MiliToHwpUnit(1.0)  # 표 안 셀 오른쪽 여백

    hwp.HAction.Execute("TableCreate", hwp.HParameterSet.HTableCreation.HSet)  # 표 삽입


# 표 속성 셋팅 함수
def setHwpTableProperty(hwp, contentsDetailType, borderStyle):
    # 글씨 크기 9pt 설정
    # hwp.HAction.Run("Cancel")  # 셀선택 해제
    # rowPosition = int(re.sub(r'[^0-9]', '', hwp.KeyIndicator()[-1][1:].split(")")[0])) #hwp.KeyIndicator()는 상태바의 정보 추출 함수
    # 1행 1열로 캐럿 옮기기
    hwp.HAction.Run("TableCellBlockRow")  # 표 현재 행 선택
    hwp.HAction.Run("TableColPageUp")  # 표 전체 선택

    setFont(hwp, 900);  # 폰트 크기 9pt로 설정

    # 표 안쪽 테두리 여부
    if borderStyle == "innerNone":
        # hwp.HAction.Run("TableCellBorderAll")
        hwp.HAction.GetDefault("CellBorder", hwp.HParameterSet.HCellBorderFill.HSet)
        hwp.HParameterSet.HCellBorderFill.TypeHorz = hwp.HwpLineType("None")
        hwp.HParameterSet.HCellBorderFill.TypeVert = hwp.HwpLineType("None")
        hwp.HParameterSet.HCellBorderFill.BorderTypeTop = hwp.HwpLineType("Solid")  # 상단 투명
        hwp.HParameterSet.HCellBorderFill.BorderTypeBottom = hwp.HwpLineType("Solid")  # 상단 투명
        hwp.HParameterSet.HCellBorderFill.BorderTypeRight = hwp.HwpLineType("Solid")  # 우측 투명
        hwp.HParameterSet.HCellBorderFill.BorderTypeLeft = hwp.HwpLineType("Solid")  # 좌측 투명
        hwp.HAction.Execute("CellBorder", hwp.HParameterSet.HCellBorderFill.HSet)
        # hwp.HAction.Run("TableCellBorderInside")  # 표 테두리 토글(있음, 없음) nx1 표에서 정상 작동 안
    elif borderStyle == "allNone":
        hwp.HAction.Run("TableCellBorderAll")  # 표 테두리 토글(있음, 없음)

    if contentsDetailType == "table":
        # 표 바깥 여백 및 글씨처럼 취급 설정
        hwp.HAction.GetDefault("ShapeObjDialog", hwp.HParameterSet.HShapeObject.HSet)
        hwp.HParameterSet.HShapeObject.HSet.SetItem("TreatAsChar", True)
        hwp.HParameterSet.HShapeObject.HSet.SetItem("OutsideMarginTop", hwp.MiliToHwpUnit(1.0))
        hwp.HParameterSet.HShapeObject.HSet.SetItem("OutsideMarginBottom", hwp.MiliToHwpUnit(1.0))
        hwp.HAction.Execute("ShapeObjDialog", hwp.HParameterSet.HShapeObject.HSet)
    elif contentsDetailType == "condBox":
        # 표 바깥 여백 및 글씨처럼 취급 설정
        hwp.HAction.GetDefault("ShapeObjDialog", hwp.HParameterSet.HShapeObject.HSet)
        hwp.HParameterSet.HShapeObject.HSet.SetItem("TreatAsChar", True)
        hwp.HParameterSet.HShapeObject.HSet.SetItem("OutsideMarginTop", hwp.MiliToHwpUnit(0.0))
        hwp.HParameterSet.HShapeObject.HSet.SetItem("OutsideMarginBottom", hwp.MiliToHwpUnit(0.0))
        hwp.HAction.Execute("ShapeObjDialog", hwp.HParameterSet.HShapeObject.HSet)


# 한컴 컨텐츠 쓰기 함수
def writeContentsForHwp(hwp, jsonObjForHwp):
    if jsonObjForHwp["contentsType"] == "img":
        insertHwpImg(hwp, jsonObjForHwp)
    elif jsonObjForHwp["contentsType"] == "text":
        insertHwpText(hwp, jsonObjForHwp);
    elif jsonObjForHwp["contentsType"] == "underLine":
        executeUnderLine(hwp)
    elif jsonObjForHwp["contentsType"] == "CharShapeBold":
        hwp.Run("CharShapeBold")
    elif jsonObjForHwp["contentsType"] == "BreakPara":
        hwp.Run("BreakPara")
    elif jsonObjForHwp["contentsType"] == "alignLeft":
        hwp.Run("ParagraphShapeAlignLeft")
    elif jsonObjForHwp["contentsType"] == "alignRight":
        hwp.Run("ParagraphShapeAlignRight")
    elif jsonObjForHwp["contentsType"] == "alignCenter":
        hwp.Run("ParagraphShapeAlignCenter")
    elif jsonObjForHwp["contentsType"] == "formul":
        insertHwpEquation(hwp, jsonObjForHwp)
    elif jsonObjForHwp["contentsType"] == "table":
        insertHwpTable(hwp, jsonObjForHwp)
        i = 0;
        for cellObj in jsonObjForHwp["contents"]:
            for cellInnerValObj in cellObj:
                writeContentsForHwp(hwp, cellInnerValObj["contents"])
            # 표 정렬
            # 실제 json 객체에는 셀 안의 contents에 대해 align 속성 있지만 셀 안의 정렬 속성 모두 같으므로 0번째 idx로만 설
            if cellObj[0]["align"] == "alignLeft":
                hwp.Run("ParagraphShapeAlignLeft")
            elif cellObj[0]["align"] == "alignRight":
                hwp.Run("ParagraphShapeAlignRight")
            else:
                hwp.Run("ParagraphShapeAlignCenter")

            i = i + 1
            if (i == len(jsonObjForHwp["contents"])):  # 마지막 셀인 경우
                # 표 속성 셋팅
                setHwpTableProperty(hwp, jsonObjForHwp["contentsDetailType"], jsonObjForHwp["borderStyle"])

                hwp.Run("CloseEx")  # 표 밖으로 빠져 나오기
                hwp.Run("MoveLineEnd")  # 표 오른쪽으로 커서 이동

                if jsonObjForHwp["contentsDetailType"] == "table":
                    hwp.Run("MoveDocEnd")
                elif jsonObjForHwp["contentsDetailType"] == "condBox":
                    # hwp 표 삽입의 경우 위아래 줄바꿈이 자동으로 되는 것 같음
                    # 조건 박스의 경우 위아래 줄바꿈 제거
                    hwp.Run("Delete")  # 표 아래 줄바꿈 제거
                    hwp.Run("MoveLineBegin")  # 표 왼쪽으로 커서 이동
                    hwp.Run("DeleteBack")  # 표 위 줄바꿈 제거
                    hwp.Run("MoveLineEnd")  # 표 뒤로 커서 이동
            else:  # 마지막 셀이 아닌 경우
                hwp.Run("TableRightCell")  # 오른쪽으로 표 셀 이동


# 고정폭 빈칸 모드
def fixedSpaceMode(hwp, findStr, replaceStr):
    hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
    hwp.HParameterSet.HFindReplace.FindString = findStr
    hwp.HParameterSet.HFindReplace.ReplaceString = replaceStr
    hwp.HParameterSet.HFindReplace.Direction = 2
    hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
    hwp.HAction.Execute("AllReplace", hwp.HParameterSet.HFindReplace.HSet)



def makeHwpController(jsonStr):
    jsonArrForHwp = json.loads(jsonStr)
    hwp = makeHwp("좁게", "alignLeft", 900, 0)
    setMultiColLayout(hwp, 2, "SOLID")

    for jsonObjForHwp in jsonArrForHwp:
        if "contentsType" in jsonObjForHwp:
            writeContentsForHwp(hwp, jsonObjForHwp)
    # 띄어쓰기 간격이 달라 연속한 띄어쓰기는 폭이 더 좁은 고정폭 띄어쓰기로 변환
    fixedSpaceMode(hwp, "   ", "^s^s^s")  # 홀수개
    fixedSpaceMode(hwp, "  ", "^s^s")  # 짝수개

    nowDate = str(datetime.now()).replace("-", "").replace(" ", "_").replace(":", "").replace(".", "_")
    randNum = str(int(random.random() * 10 ** 9))
    hwpFileName = "[N명의수학]나의 제작문제" + "_" + nowDate + "_" + randNum + ".hwp"
    hwp.SaveAs(os.getcwd() + "\\userHwp\\" + hwpFileName)  # 기존 파일명+_n.hwp 로 저장"
    hwp.XHwpDocuments.Item(0).Close(isDirty=False)  # 탭 닫기
    time.sleep(0.2)  # 0.2초 쉬어줌(꼭 필요)
    hwp.Quit()

    return os.getcwd() + "\\userHwp\\" + hwpFileName


def convertFormulToText(filename):
    BASE_DIR = os.getcwd() + "\\convertHwp"
    # 한/글 열기
    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject", pythoncom.CoInitialize())
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckModule")
    hwp.XHwpWindows.Item(0).Visible = False
    hwp.Open(os.path.join(BASE_DIR, filename))
    #확장자가 hwp가 아닌 경우 hwp로 포맷 변환하고 hwp파일로 편집하기
    path, ext = os.path.splitext(filename)
    if ext == ".hml" or ext == ".hwt" or ext == ".hwpx" or ext == ".hwtx" :
        hwp.SaveAs(BASE_DIR+"\\"+path+".hwp")
        hwp.Save()
        time.sleep(0.2)  # 0.2초 쉬어줌(꼭 필요)
        hwp.Quit()
        #기존 hwp확장자 아닌 한글 파일 제거
        os.remove(BASE_DIR+"\\"+ filename)
        #새로운 hwp파일로 편집 시작
        filename = path + ".hwp"
        hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject", pythoncom.CoInitialize())
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckModule")
        hwp.XHwpWindows.Item(0).Visible = False
        hwp.Open(os.path.join(BASE_DIR, filename))



    # 주석 저장(각주, 미주)
    nowDate = str(datetime.now()).replace("-", "").replace(" ", "_").replace(":", "").replace(".", "_")
    randNum = str(int(random.random() * 10 ** 9))
    fileName = nowDate + "_" + randNum + ".hwp"
    hwp.HAction.GetDefault("SaveFootnote", hwp.HParameterSet.HSaveFootnote.HSet)
    fileName = os.getcwd() + "\\convertHeaderFooterHwp\\" + fileName
    hwp.HParameterSet.HSaveFootnote.HSet.SetItem('FileName', fileName)
    hwp.HParameterSet.HSaveFootnote.HSet.SetItem('Flag', 3)
    existFootNote = hwp.HAction.Execute("SaveFootnote", hwp.HParameterSet.HSaveFootnote.HSet)
    time.sleep(0.2)  # 0.2초 쉬어줌(꼭 필요)

    if(existFootNote):
        # 제일 하단에 주석(각주, 미주) 추가
        hwp.Run('MoveDocEnd')
        hwp.Run('BreakPara')
        hwp.HAction.GetDefault("InsertFile", hwp.HParameterSet.HInsertFile.HSet);
        option = hwp.HParameterSet.HInsertFile
        option.filename = fileName
        option.KeepSection = 0;
        option.KeepCharshape = 1;
        option.KeepParashape = 1;
        option.KeepStyle = 1;
        hwp.HAction.Execute("InsertFile", hwp.HParameterSet.HInsertFile.HSet);
        time.sleep(0.2)  # 0.2초 쉬어줌(꼭 필요)

        # 모든 각주를 미주로 변환
        hwp.HAction.GetDefault("ExchangeFootnoteEndnote", hwp.HParameterSet.HExchangeFootnoteEndNote.HSet)
        hwp.HParameterSet.HExchangeFootnoteEndNote.Flag = 0
        hwp.HAction.Execute("ExchangeFootnoteEndnote", hwp.HParameterSet.HExchangeFootnoteEndNote.HSet)

        # 머리말, 꼬리말, 미주 지우기
        hwp.HAction.GetDefault("DeleteCtrls", hwp.HParameterSet.HDeleteCtrls.HSet)
        hwp.HParameterSet.HDeleteCtrls.CreateItemArray('DeleteCtrlType', 3)
        hwp.HParameterSet.HDeleteCtrls.DeleteCtrlType.SetItem(0, 31)  # 전체 머리말 지우기
        hwp.HParameterSet.HDeleteCtrls.DeleteCtrlType.SetItem(1, 26)  # 전체 꼬리말 지우기
        hwp.HParameterSet.HDeleteCtrls.DeleteCtrlType.SetItem(2, 14)  # 전체 미주 지우기
        hwp.HAction.Execute("DeleteCtrls", hwp.HParameterSet.HDeleteCtrls.HSet)

        #주석 파일 제거
        os.remove(fileName)
        time.sleep(0.2)  # 0.2초 쉬어줌(꼭 필요)

    #수식 가공 시작
    hwp.Run('MoveDocBegin')
    """
    ctrl = hwp.HeadCtrl
    while ctrl != None:
        if ctrl.CtrlID == "eqed":
            position = ctrl.GetAnchorPos(0)  # 해당 컨트롤의 좌표를 position 변수에 저장
            position = position.Item("List"), position.Item("Para"), position.Item("Pos")
            hwp.SetPos(*position)  # 해당 컨트롤 앞으로 캐럿(커서)을 옮김
            hwp.FindCtrl()
            액션 = hwp.CreateAction("EquationModify")
            세트 = 액션.CreateSet()
            아이템셋 = 세트.CreateItemSet("EqEdit", "EqEdit")
            액션.GetDefault(아이템셋)
            추출수식 = 아이템셋.Item("VisualString").replace("\r\n", " ")
            hwp.Run("Delete")
            if (추출수식 != ""):
                hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet);
                hwp.HParameterSet.HInsertText.Text = "$strt/ " + 추출수식 + " $end/";
                hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet);
                hwp.Run("MoveLineBegin")
        ctrl = ctrl.Next
    """
    hwp.RunScriptMacro("OnScriptMacro_equationToTexScript()", 0, 1)
    time.sleep(0.2)  # 0.2초 쉬어줌(꼭 필요)
    hwp.Run('MoveDocBegin')
    time.sleep(0.2)  # 0.2초 쉬어줌(꼭 필요)
    hwp.RunScriptMacro("OnScriptMacro_zocboCirlcleImg()", 0, 1)
    time.sleep(0.2)  # 0.2초 쉬어줌(꼭 필요)

    #줄바꿈 처리 안되는 에러 해결
    hwp.Run('MoveDocBegin')
    hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
    hwp.HParameterSet.HFindReplace.FindString = "^l"     #강제 줄나눔
    hwp.HParameterSet.HFindReplace.ReplaceString = "^n"  #문단 끝
    hwp.HParameterSet.HFindReplace.Direction = 2
    hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
    hwp.HAction.Execute("AllReplace", hwp.HParameterSet.HFindReplace.HSet)

    #절댓값 변경(web에서 이 문자 못 받아들임)
    hwp.Run('MoveDocBegin')
    hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
    hwp.HParameterSet.HFindReplace.FindString = ""
    hwp.HParameterSet.HFindReplace.ReplaceString = "|"
    hwp.HParameterSet.HFindReplace.Direction = 2
    hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
    hwp.HAction.Execute("AllReplace", hwp.HParameterSet.HFindReplace.HSet)

    # 평행기호 변경(web에서 이 문자 못 받아들임)
    hwp.Run('MoveDocBegin')
    hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
    hwp.HParameterSet.HFindReplace.FindString = "󰁚"
    hwp.HParameterSet.HFindReplace.ReplaceString = "//"
    hwp.HParameterSet.HFindReplace.Direction = 2
    hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
    hwp.HAction.Execute("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
    
    # 닮음기호 변경(web에서 이 문자 못 받아들임)
    hwp.Run('MoveDocBegin')
    hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
    hwp.HParameterSet.HFindReplace.FindString = "󰁀"
    hwp.HParameterSet.HFindReplace.ReplaceString = "∽"
    hwp.HParameterSet.HFindReplace.Direction = 2
    hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
    hwp.HAction.Execute("AllReplace", hwp.HParameterSet.HFindReplace.HSet)

    # 한컴 띄어쓰기 변경(web에서 이 문자 못 받아들임)
    hwp.Run('MoveDocBegin')
    hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
    hwp.HParameterSet.HFindReplace.FindString = ""
    hwp.HParameterSet.HFindReplace.ReplaceString = " "
    hwp.HParameterSet.HFindReplace.Direction = 2
    hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
    hwp.HAction.Execute("AllReplace", hwp.HParameterSet.HFindReplace.HSet)

    # 한컴 띄어쓰기 변경(web에서 이 문자 못 받아들임)
    hwp.Run('MoveDocBegin')
    hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
    hwp.HParameterSet.HFindReplace.FindString = ""
    hwp.HParameterSet.HFindReplace.ReplaceString = " "
    hwp.HParameterSet.HFindReplace.Direction = 2
    hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
    hwp.HAction.Execute("AllReplace", hwp.HParameterSet.HFindReplace.HSet)

    # 한컴 띄어쓰기 변경(web에서 이 문자 못 받아들임)
    hwp.Run('MoveDocBegin')
    hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
    hwp.HParameterSet.HFindReplace.FindString = ""
    hwp.HParameterSet.HFindReplace.ReplaceString = " "
    hwp.HParameterSet.HFindReplace.Direction = 2
    hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
    hwp.HAction.Execute("AllReplace", hwp.HParameterSet.HFindReplace.HSet)

    hwp.Run("SelectAll")
    char_shape = hwp.CharShape
    char_shape.SetItem("UseFontSpace", 0)
    char_shape.SetItem("Height", 900)
    hwp.CharShape = char_shape
    hwp.Run(f"CharShapeTextColor{'black'}")

    hwp.Save()
    time.sleep(0.2)  # 0.2초 쉬어줌(꼭 필요)
    hwp.Quit()

    #hwp to html
    exefile = 'hwp5html'
    folderName = BASE_DIR + "\\" + filename.split(".hwp")[0]
    os.system(exefile+" "+BASE_DIR+"\\"+filename+" --output "+folderName)
    time.sleep(0.2)  # 0.2초 쉬어줌(꼭 필요)
    #hwp파일 삭제
    os.remove(BASE_DIR+"\\"+filename)
    time.sleep(0.2)  # 0.2초 쉬어줌(꼭 필요)


    """
    similarArr = []
    # 원형문자 이미지 제외하고 base64로 디코딩
    imgFileList = os.listdir(folderName+"\\binData")
    circleImgList = os.listdir(os.getcwd() + "\\convertCompareImg")
    for item in imgFileList:
        for circleImg in circleImgList:
            if item.endswith(".jpg") or item.endswith(".png") or item.endswith(".bmp"):
                similarVal = commonUtil.pixelDiff(os.getcwd()+"\\convertCompareImg\\"+circleImg, folderName+"\\binData\\"+item)
                if(similarVal<5):
                    similarArr.append({"circleType":circleImg.split(".")[0], "filePath":item})
                    break

    page = open(folderName+'/index.xhtml', 'rt', encoding='utf-8').read()
    soup = BeautifulSoup(page, 'html.parser')
    for circleImg in similarArr:
        for img in soup.find_all('img', src="bindata/"+circleImg["filePath"]):
            img["class"] = "circle "+circleImg["circleType"]

    for circleImg in similarArr:
        os.remove(folderName+"/bindata/"+circleImg["filePath"])
    """

    """
    #이미지 base64 인코딩
    for img in soup.find_all('img'):
        with open(folderName+"\\"+img["src"], 'rb') as images:
            base64_string = base64.b64encode(images.read())
            img["src"] = "data:image/png;base64,"+str(base64_string, 'utf-8')
    """
    """
    file = open(folderName + '/index.xhtml', 'w', encoding='utf-8')
    file.write(soup.prettify())
    file.close()
    """
    #css파일 제거
    cssFileList = os.listdir(folderName)
    for item in cssFileList:
        if item.endswith(".css"):
            os.remove(os.path.join(folderName, item))

    # zip파일 만들기
    shutil.make_archive(folderName, 'zip', folderName)

    return folderName

