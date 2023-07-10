package main

import "C"
import "unsafe"

type moduleInfo struct {
	sensorId          string
	barcode           string
	temporaryModuleId int64
}

func IsEmpty(val string) bool {
	return len([]rune(val)) == 0 || val == "0"
}

//export MakeTemporaryModuleIdGo
func MakeTemporaryModuleIdGo(sensorId []*C.char, barcode []*C.char) uintptr {

	arraySensorIdGo := make([]string, 0)
	for _, _val := range sensorId {
		temp := C.GoString(_val) // to go string(copy)
		arraySensorIdGo = append(arraySensorIdGo, temp)
	}
	arrayBarcodeGo := make([]string, 0)
	for _, _val := range barcode {
		temp := C.GoString(_val) // to go string(copy)
		arrayBarcodeGo = append(arrayBarcodeGo, temp)
	}

	moduleList := make([]moduleInfo, 0)
	result := make([]int64, len(arraySensorIdGo))

	for idx, _ := range arraySensorIdGo {
		existTemporaryModuleId := false
		if !IsEmpty(arraySensorIdGo[idx]) && !existTemporaryModuleId {
			for idxInModuleList, module := range moduleList {
				if module.sensorId != arraySensorIdGo[idx] {
					continue
				}
				existTemporaryModuleId = true
				result[idx] = module.temporaryModuleId
				if !IsEmpty(arrayBarcodeGo[idx]) && IsEmpty(module.barcode) {
					moduleList[idxInModuleList].barcode = arrayBarcodeGo[idx]
				}
			}
		}

		if !IsEmpty(arrayBarcodeGo[idx]) && !existTemporaryModuleId {
			for idxInModuleList, module := range moduleList {
				if module.barcode != arrayBarcodeGo[idx] {
					continue
				}
				existTemporaryModuleId = true
				result[idx] = module.temporaryModuleId
				if !IsEmpty(arraySensorIdGo[idx]) && IsEmpty(module.sensorId) {
					moduleList[idxInModuleList].sensorId = arraySensorIdGo[idx]
				}

			}
		}

		if existTemporaryModuleId {
			continue
		}
		numTemporaryModuleId := int64(len(moduleList) + 1)
		result[idx] = numTemporaryModuleId
		moduleList = append(moduleList, moduleInfo{sensorId: arraySensorIdGo[idx], barcode: arrayBarcodeGo[idx], temporaryModuleId: numTemporaryModuleId})
	}

	return uintptr(unsafe.Pointer(&result[0]))
}

func main() {}
