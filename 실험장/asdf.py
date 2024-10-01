










for u in range(0, len(uDraws)):         # u 방향 b spline
        interval = uIntervals[u]
        tempIndex = interval + 1                                        # 계산식에서 인덱스를 맞추기 위해 쓰는 임시 변수
        
        
        tempCps = [arr[:] for arr in cps]                               # 계산값 임시 저장 리스트 1

        for height in range(0, len(tempCps)):
            
            
            for k in range(1, degree + 1):              # degree 인덱스 k
                temp = [vec2d(0, 0) for i in range(0, len(cps))]            # 계산값 임시 저장 리스트 2
                iInitial = interval - degree + k + 1    # control points 계산 결과들의 인덱스 i의 초기값 (degree마다 바뀜)
                
                for i in range(iInitial, interval + 2):                                         # i부터 최대값까지 반복 계산
                    alpha = (uDraws[u] - knts[i - 1]) / (knts[i + degree - k] - knts[i - 1])            # 계수
                    
                    temp[i] = (1 - alpha) * tempCps[height][i - 1] + alpha * tempCps[height][i]         # 결과가 인덱스 (interval+1)로 모이도록 임시 저장
                
                tempCps[height] = list(temp)        # temp에 임시저장한 계산 결과를 tempCps로 옮김
                
            
            
            
            uResult[height].append(tempCps[height][tempIndex])