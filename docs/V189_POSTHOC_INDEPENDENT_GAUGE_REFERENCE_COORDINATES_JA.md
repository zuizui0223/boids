# v189｜独立する2006年RWS公式文献と2011年WEBTICSの観測局座標比較

**After v188 spatial positive result, explicitly a posthoc, source-only robustness diagnostic.** 2006年報告書の独立した真正な印刷付録を発見したため、2026年11月18日に全15観測所の公開RD平面位置をデジタル転記して2011年WEBTICS附表との一致を数える。**2018–19年のRWS原装置位置を保証しない。**

- Rijkswaterstaat RIKZ/2006.012, *Waterstanden Nederlandse kust en estuaria*, date 27 June 2006, Appendix 2 printed p.69, <https://www.vliz.be/imisdocs/publications/282819.pdf>
- Rappoldt & Ens (2011) EcoCurves/SOVON WEBTICS, Appendix A Table A.1 printed p.46, <https://nam-feitenencijfers.data-app.nl/download/rapport/d360edf8-1955-4ee4-b0e9-58826d7e0a53?open=true>

15共通地点の位置差をEPSG:28992のユークリッド距離で計算する。v188の13点LOO幾何も、原報告書2006年位置へ入れ替えた場合の最寄り局、IDW3の距離重み、三角形内側/外側を比較する。**水位値はこの版で一切開かない**。参照表の転記はPDFからの手入力であり、原PDFバイナリ自体のSHAはこのスクリプトでは検証しない。

たとえ参照位置が一致しても、`denhelder.marsdiep`等の特定された**2018/19原RWS station code**が2006年のDen Helder局と厳密に同じ場所・装置だった証拠にはならない。個別原GPS地点の局所潮位、標高zの鉛直NAP、測量日、潮汐×太陽による採餌因果もすべてNOT_ADMITTED。

`PYTHONPATH=validation_v110:validation_v183:validation_v185:validation_v187:validation_v188 python -m unittest discover -s validation_v189 -p 'test_*.py'`。
