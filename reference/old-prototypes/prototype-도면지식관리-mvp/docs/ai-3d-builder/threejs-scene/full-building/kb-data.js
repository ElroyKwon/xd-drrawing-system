export default {
  "sheets": [
    {
      "sheet_id": "arch_p060",
      "sheet_number": "A04.01",
      "source_png": "D:\\_Project\\prototype-도면지식관리-mvp\\dwg\\1) 건축공사\\0. PDF 도면\\_png_dpi400\\arch_p060.png",
      "discipline": "architectural",
      "extraction_source": "D:/_Project/prototype-도면지식관리-mvp/docs/ai-3d-builder/outputs/2026-04-22_084228_arch_p060_gemini-3.1-flash-image_agent/stage-10-parsed.json",
      "global_confidence": 0.8,
      "views": [
        {
          "view_id": "v1",
          "view_label": "지상1층 확대평면도-1",
          "view_scale": "1/200(A3)",
          "level": {
            "name": "지상1층",
            "elevation_mm": null,
            "ceiling_height_mm": null
          },
          "grid": {
            "x_labels": [
              "1",
              "2",
              "2A",
              "3",
              "4"
            ],
            "y_labels": [
              "A",
              "B",
              "B1",
              "B2",
              "C",
              "D"
            ],
            "x_spacings_mm": [
              12000,
              4700,
              7300,
              12000
            ],
            "y_spacings_mm": [
              13000,
              6950,
              4100,
              5950,
              13000
            ],
            "x_direction": "left_to_right",
            "y_direction": "top_to_bottom"
          },
          "grid_validation": {
            "x_spacings_sum_mm": 36000,
            "y_spacings_sum_mm": 43000,
            "x_labels_count": 5,
            "y_labels_count": 6,
            "x_spacings_count": 4,
            "y_spacings_count": 5,
            "x_labels_vs_spacings_ok": true,
            "y_labels_vs_spacings_ok": true
          },
          "anchored_counts": {
            "rooms": {
              "total": 6,
              "anchored": 6,
              "pct": 100.0
            },
            "walls": {
              "total": 4,
              "anchored": 4,
              "pct": 100.0
            },
            "cores": {
              "total": 1,
              "anchored": 1,
              "pct": 100.0
            },
            "voids": {
              "total": 0
            },
            "doors": {
              "total": 0
            },
            "columns": {
              "total": 8
            },
            "dims": {
              "total": 37,
              "anchored": 9,
              "pct": 24.3
            }
          },
          "elements": [
            {
              "id": "r1",
              "type": "room",
              "polygon_grid": [
                [
                  "1",
                  "A"
                ],
                [
                  "2",
                  "A"
                ],
                [
                  "2",
                  "B"
                ],
                [
                  "1",
                  "B"
                ]
              ],
              "name": "진동시험실",
              "area_m2": null,
              "confidence": 0.9
            },
            {
              "id": "r2",
              "type": "room",
              "polygon_grid": [
                [
                  "2",
                  "A"
                ],
                [
                  "2A",
                  "A"
                ],
                [
                  "2A",
                  "B"
                ],
                [
                  "2",
                  "B"
                ]
              ],
              "name": "제어룸",
              "area_m2": null,
              "confidence": 0.9
            },
            {
              "id": "r3",
              "type": "room",
              "polygon_grid": [
                [
                  "2A",
                  "A"
                ],
                [
                  "3",
                  "A"
                ],
                [
                  "3",
                  "B"
                ],
                [
                  "2A",
                  "B"
                ]
              ],
              "name": "환경시험실",
              "area_m2": null,
              "confidence": 0.9
            },
            {
              "id": "r4",
              "type": "room",
              "polygon_grid": [
                [
                  "1",
                  "C"
                ],
                [
                  "2",
                  "C"
                ],
                [
                  "2",
                  "D"
                ],
                [
                  "1",
                  "D"
                ]
              ],
              "name": "대용량 모터부하설",
              "area_m2": null,
              "confidence": 0.9
            },
            {
              "id": "r5",
              "type": "room",
              "polygon_grid": [
                [
                  "2",
                  "C"
                ],
                [
                  "3",
                  "C"
                ],
                [
                  "3",
                  "D"
                ],
                [
                  "2",
                  "D"
                ]
              ],
              "name": "시험 전원실",
              "area_m2": null,
              "confidence": 0.9
            },
            {
              "id": "r6",
              "type": "room",
              "polygon_grid": [
                [
                  "2",
                  "C"
                ],
                [
                  "2A",
                  "C"
                ],
                [
                  "2A",
                  "D"
                ],
                [
                  "2",
                  "D"
                ]
              ],
              "name": "부하 제어 및 기능시험실",
              "area_m2": null,
              "confidence": 0.9
            },
            {
              "id": "w1",
              "type": "wall",
              "path_grid": [
                [
                  "1",
                  "A"
                ],
                [
                  "4",
                  "A"
                ]
              ],
              "thickness_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "w2",
              "type": "wall",
              "path_grid": [
                [
                  "1",
                  "D"
                ],
                [
                  "4",
                  "D"
                ]
              ],
              "thickness_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "w3",
              "type": "wall",
              "path_grid": [
                [
                  "1",
                  "A"
                ],
                [
                  "1",
                  "D"
                ]
              ],
              "thickness_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "w4",
              "type": "wall",
              "path_grid": [
                [
                  "4",
                  "A"
                ],
                [
                  "4",
                  "D"
                ]
              ],
              "thickness_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c1",
              "type": "column",
              "at_grid": [
                "1",
                "A"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "c2",
              "type": "column",
              "at_grid": [
                "2",
                "A"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "c3",
              "type": "column",
              "at_grid": [
                "3",
                "A"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "c4",
              "type": "column",
              "at_grid": [
                "4",
                "A"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "c5",
              "type": "column",
              "at_grid": [
                "1",
                "D"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "c6",
              "type": "column",
              "at_grid": [
                "2",
                "D"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "c7",
              "type": "column",
              "at_grid": [
                "3",
                "D"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "c8",
              "type": "column",
              "at_grid": [
                "4",
                "D"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "st1",
              "type": "stair",
              "at_grid": [
                "2",
                "D"
              ],
              "label": "원형 스텝프 조면처리",
              "confidence": 0.8
            }
          ],
          "dimensions_raw": [
            {
              "text": "12,000",
              "from_grid": [
                "1",
                "A"
              ],
              "to_grid": [
                "2",
                "A"
              ]
            },
            {
              "text": "4,700",
              "from_grid": [
                "2",
                "A"
              ],
              "to_grid": [
                "2A",
                "A"
              ]
            },
            {
              "text": "7,300",
              "from_grid": [
                "2A",
                "A"
              ],
              "to_grid": [
                "3",
                "A"
              ]
            },
            {
              "text": "12,000",
              "from_grid": [
                "3",
                "A"
              ],
              "to_grid": [
                "4",
                "A"
              ]
            },
            {
              "text": "13,000",
              "from_grid": [
                "A",
                "1"
              ],
              "to_grid": [
                "B",
                "1"
              ]
            },
            {
              "text": "6,950",
              "from_grid": [
                "B",
                "1"
              ],
              "to_grid": [
                "B1",
                "1"
              ]
            },
            {
              "text": "4,100",
              "from_grid": [
                "B1",
                "1"
              ],
              "to_grid": [
                "B2",
                "1"
              ]
            },
            {
              "text": "5,950",
              "from_grid": [
                "B2",
                "1"
              ],
              "to_grid": [
                "C",
                "1"
              ]
            },
            {
              "text": "13,000",
              "from_grid": [
                "C",
                "1"
              ],
              "to_grid": [
                "D",
                "1"
              ]
            },
            {
              "text": "6,000",
              "from_grid": [
                "1",
                "A"
              ],
              "to_grid": null
            },
            {
              "text": "3,925",
              "from_grid": [
                "2",
                "A"
              ],
              "to_grid": null
            },
            {
              "text": "6,250",
              "from_grid": [
                "1",
                "B"
              ],
              "to_grid": null
            },
            {
              "text": "4,200",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "550",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "13,500",
              "from_grid": [
                "2A",
                "B"
              ],
              "to_grid": null
            },
            {
              "text": "3,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "6,200",
              "from_grid": null,
              "to_grid": [
                "4",
                "B"
              ]
            },
            {
              "text": "9,500",
              "from_grid": [
                "1",
                "C"
              ],
              "to_grid": null
            },
            {
              "text": "2,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "8,400",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3,850",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,500",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3,750",
              "from_grid": null,
              "to_grid": [
                "4",
                "C"
              ]
            },
            {
              "text": "16,494",
              "from_grid": [
                "1",
                "D"
              ],
              "to_grid": null
            },
            {
              "text": "2,750",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "300",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,825",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "550",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "5,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "550",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,450",
              "from_grid": null,
              "to_grid": [
                "4",
                "D"
              ]
            },
            {
              "text": "12,600",
              "from_grid": [
                "2",
                "D"
              ],
              "to_grid": null
            },
            {
              "text": "4,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3,400",
              "from_grid": null,
              "to_grid": [
                "4",
                "D"
              ]
            }
          ],
          "annotations_ko": [
            "상부 CANOPY",
            "극한환경시험실",
            "전기차/반도체/2차전지 In-Line 검증시스템",
            "THK6 CHECKED PALTE",
            "트렌치 (550X250)",
            "원형 스텝프 조면처리"
          ],
          "unresolved": []
        },
        {
          "view_id": "v2",
          "view_label": "PIT 확대평면도",
          "view_scale": "1/200(A3)",
          "level": {
            "name": "PIT",
            "elevation_mm": null,
            "ceiling_height_mm": null
          },
          "grid": {
            "x_labels": [
              "5",
              "5A",
              "5B",
              "6"
            ],
            "y_labels": [
              "B1",
              "B2",
              "C",
              "D"
            ],
            "x_spacings_mm": [
              2000,
              6125,
              2875
            ],
            "y_spacings_mm": [
              10050,
              13000
            ],
            "x_direction": "left_to_right",
            "y_direction": "top_to_bottom"
          },
          "grid_validation": {
            "x_spacings_sum_mm": 11000,
            "y_spacings_sum_mm": 23050,
            "x_labels_count": 4,
            "y_labels_count": 4,
            "x_spacings_count": 3,
            "y_spacings_count": 2,
            "x_labels_vs_spacings_ok": true,
            "y_labels_vs_spacings_ok": false
          },
          "anchored_counts": {
            "rooms": {
              "total": 1,
              "anchored": 1,
              "pct": 100.0
            },
            "walls": {
              "total": 4,
              "anchored": 4,
              "pct": 100.0
            },
            "cores": {
              "total": 0,
              "anchored": 0,
              "pct": 0.0
            },
            "voids": {
              "total": 0
            },
            "doors": {
              "total": 0
            },
            "columns": {
              "total": 4
            },
            "dims": {
              "total": 9,
              "anchored": 6,
              "pct": 66.7
            }
          },
          "elements": [
            {
              "id": "r7",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "B1"
                ],
                [
                  "6",
                  "B1"
                ],
                [
                  "6",
                  "D"
                ],
                [
                  "5",
                  "D"
                ]
              ],
              "name": "PIT",
              "area_m2": null,
              "confidence": 0.9
            },
            {
              "id": "w5",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "B1"
                ],
                [
                  "6",
                  "B1"
                ]
              ],
              "thickness_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "w6",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "D"
                ],
                [
                  "6",
                  "D"
                ]
              ],
              "thickness_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "w7",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "B1"
                ],
                [
                  "5",
                  "D"
                ]
              ],
              "thickness_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "w8",
              "type": "wall",
              "path_grid": [
                [
                  "6",
                  "B1"
                ],
                [
                  "6",
                  "D"
                ]
              ],
              "thickness_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c9",
              "type": "column",
              "at_grid": [
                "5",
                "B1"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "c10",
              "type": "column",
              "at_grid": [
                "6",
                "B1"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "c11",
              "type": "column",
              "at_grid": [
                "5",
                "D"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "c12",
              "type": "column",
              "at_grid": [
                "6",
                "D"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            }
          ],
          "dimensions_raw": [
            {
              "text": "11,500",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "6",
                "B1"
              ]
            },
            {
              "text": "2,000",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5A",
                "B1"
              ]
            },
            {
              "text": "6,125",
              "from_grid": [
                "5A",
                "B1"
              ],
              "to_grid": [
                "5B",
                "B1"
              ]
            },
            {
              "text": "2,875",
              "from_grid": [
                "5B",
                "B1"
              ],
              "to_grid": [
                "6",
                "B1"
              ]
            },
            {
              "text": "10,050",
              "from_grid": [
                "B1",
                "5"
              ],
              "to_grid": [
                "C",
                "5"
              ]
            },
            {
              "text": "13,000",
              "from_grid": [
                "C",
                "5"
              ],
              "to_grid": [
                "D",
                "5"
              ]
            },
            {
              "text": "1,950",
              "from_grid": [
                "B1",
                "5"
              ],
              "to_grid": null
            },
            {
              "text": "2,150",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "5,950",
              "from_grid": null,
              "to_grid": [
                "C",
                "5"
              ]
            }
          ],
          "annotations_ko": [
            "PIT 점검사다리",
            "상부점검구(0.9X0.8)",
            "SLOPE",
            "SUMPPIT(0.9X0.9X0.9)"
          ],
          "unresolved": []
        }
      ]
    },
    {
      "sheet_id": "arch_p061",
      "sheet_number": "A04.02",
      "source_png": "D:\\_Project\\prototype-도면지식관리-mvp\\dwg\\1) 건축공사\\0. PDF 도면\\_png_dpi400\\arch_p061.png",
      "discipline": "architectural",
      "extraction_source": "D:/_Project/prototype-도면지식관리-mvp/docs/ai-3d-builder/outputs/2026-04-22_084253_arch_p061_gemini-3.1-flash-image_agent/stage-10-parsed.json",
      "global_confidence": 0.9,
      "views": [
        {
          "view_id": "v1",
          "view_label": "지상1층 확대평면도-2",
          "view_scale": "1/200(A3)",
          "level": {
            "name": "지상1층",
            "elevation_mm": 0,
            "ceiling_height_mm": null
          },
          "grid": {
            "x_labels": [
              "4",
              "5",
              "5A",
              "5B",
              "6",
              "7"
            ],
            "y_labels": [
              "A",
              "B",
              "B1",
              "B2",
              "C",
              "D"
            ],
            "x_spacings_mm": [
              14000,
              2000,
              6125,
              2875,
              10000
            ],
            "y_spacings_mm": [
              13000,
              6950,
              4100,
              5950,
              13000
            ],
            "x_direction": "left_to_right",
            "y_direction": "top_to_bottom"
          },
          "grid_validation": {
            "x_spacings_sum_mm": 35000,
            "y_spacings_sum_mm": 43000,
            "x_labels_count": 6,
            "y_labels_count": 6,
            "x_spacings_count": 5,
            "y_spacings_count": 5,
            "x_labels_vs_spacings_ok": true,
            "y_labels_vs_spacings_ok": true
          },
          "anchored_counts": {
            "rooms": {
              "total": 7,
              "anchored": 7,
              "pct": 100.0
            },
            "walls": {
              "total": 0,
              "anchored": 0,
              "pct": 0.0
            },
            "cores": {
              "total": 3,
              "anchored": 2,
              "pct": 66.7
            },
            "voids": {
              "total": 0
            },
            "doors": {
              "total": 0
            },
            "columns": {
              "total": 16
            },
            "dims": {
              "total": 10,
              "anchored": 10,
              "pct": 100.0
            }
          },
          "elements": [
            {
              "id": "c1",
              "type": "column",
              "at_grid": [
                "4",
                "A"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c2",
              "type": "column",
              "at_grid": [
                "5",
                "A"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c3",
              "type": "column",
              "at_grid": [
                "6",
                "A"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c4",
              "type": "column",
              "at_grid": [
                "7",
                "A"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c5",
              "type": "column",
              "at_grid": [
                "4",
                "B"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c6",
              "type": "column",
              "at_grid": [
                "5",
                "B"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c7",
              "type": "column",
              "at_grid": [
                "6",
                "B"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c8",
              "type": "column",
              "at_grid": [
                "7",
                "B"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c9",
              "type": "column",
              "at_grid": [
                "4",
                "C"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c10",
              "type": "column",
              "at_grid": [
                "5",
                "C"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c11",
              "type": "column",
              "at_grid": [
                "6",
                "C"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c12",
              "type": "column",
              "at_grid": [
                "7",
                "C"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c13",
              "type": "column",
              "at_grid": [
                "4",
                "D"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c14",
              "type": "column",
              "at_grid": [
                "5",
                "D"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c15",
              "type": "column",
              "at_grid": [
                "6",
                "D"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "c16",
              "type": "column",
              "at_grid": [
                "7",
                "D"
              ],
              "size_mm": {
                "w": 600,
                "d": 600
              },
              "label": null,
              "confidence": 0.9
            },
            {
              "id": "r1",
              "type": "room",
              "polygon_grid": [
                [
                  "4",
                  "A"
                ],
                [
                  "5",
                  "A"
                ],
                [
                  "5",
                  "B"
                ],
                [
                  "4",
                  "B"
                ]
              ],
              "name": "EMI/EMS Shield실",
              "area_m2": null,
              "confidence": 0.8
            },
            {
              "id": "r2",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "A"
                ],
                [
                  "6",
                  "A"
                ],
                [
                  "6",
                  "B"
                ],
                [
                  "5",
                  "B"
                ]
              ],
              "name": "EMC 챔버실",
              "area_m2": null,
              "confidence": 0.8
            },
            {
              "id": "r3",
              "type": "room",
              "polygon_grid": [
                [
                  "4",
                  "B"
                ],
                [
                  "5",
                  "B"
                ],
                [
                  "5",
                  "C"
                ],
                [
                  "4",
                  "C"
                ]
              ],
              "name": "Drive 기능시험실",
              "area_m2": null,
              "confidence": 0.8
            },
            {
              "id": "r4",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "B"
                ],
                [
                  "6",
                  "B"
                ],
                [
                  "6",
                  "C"
                ],
                [
                  "5",
                  "C"
                ]
              ],
              "name": "고객 대기실-1,2,3",
              "area_m2": null,
              "confidence": 0.8
            },
            {
              "id": "r5",
              "type": "room",
              "polygon_grid": [
                [
                  "4",
                  "C"
                ],
                [
                  "5",
                  "C"
                ],
                [
                  "5",
                  "D"
                ],
                [
                  "4",
                  "D"
                ]
              ],
              "name": "PLC/Drive 및 신사업 검증시스템",
              "area_m2": null,
              "confidence": 0.8
            },
            {
              "id": "r6",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "C"
                ],
                [
                  "6",
                  "C"
                ],
                [
                  "6",
                  "D"
                ],
                [
                  "5",
                  "D"
                ]
              ],
              "name": "Drive 시험실",
              "area_m2": null,
              "confidence": 0.8
            },
            {
              "id": "r7",
              "type": "room",
              "polygon_grid": [
                [
                  "6",
                  "B"
                ],
                [
                  "7",
                  "B"
                ],
                [
                  "7",
                  "C"
                ],
                [
                  "6",
                  "C"
                ]
              ],
              "name": "고객 접견실",
              "area_m2": null,
              "confidence": 0.8
            },
            {
              "id": "st1",
              "type": "stair",
              "on_wall_from": [
                "5",
                "B"
              ],
              "on_wall_to": [
                "5A",
                "B"
              ],
              "offset_from_first_mm": null,
              "width_mm": null,
              "label": "계단실",
              "confidence": 0.9
            },
            {
              "id": "sh1",
              "type": "shaft",
              "at_grid": [
                "5A",
                "B"
              ],
              "size_mm": {
                "w": null,
                "d": null
              },
              "label": "PS",
              "confidence": 0.8
            },
            {
              "id": "sh2",
              "type": "shaft",
              "at_grid": [
                "5A",
                "B"
              ],
              "size_mm": {
                "w": null,
                "d": null
              },
              "label": "EPS/TPS",
              "confidence": 0.8
            }
          ],
          "dimensions_raw": [
            {
              "text": "14,000",
              "from_grid": [
                "4",
                "A"
              ],
              "to_grid": [
                "5",
                "A"
              ]
            },
            {
              "text": "2,000",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "5A",
                "A"
              ]
            },
            {
              "text": "6,125",
              "from_grid": [
                "5A",
                "A"
              ],
              "to_grid": [
                "5B",
                "A"
              ]
            },
            {
              "text": "2,875",
              "from_grid": [
                "5B",
                "A"
              ],
              "to_grid": [
                "6",
                "A"
              ]
            },
            {
              "text": "10,000",
              "from_grid": [
                "6",
                "A"
              ],
              "to_grid": [
                "7",
                "A"
              ]
            },
            {
              "text": "13,000",
              "from_grid": [
                "4",
                "A"
              ],
              "to_grid": [
                "4",
                "B"
              ]
            },
            {
              "text": "6,950",
              "from_grid": [
                "4",
                "B"
              ],
              "to_grid": [
                "4",
                "B1"
              ]
            },
            {
              "text": "4,100",
              "from_grid": [
                "4",
                "B1"
              ],
              "to_grid": [
                "4",
                "B2"
              ]
            },
            {
              "text": "5,950",
              "from_grid": [
                "4",
                "B2"
              ],
              "to_grid": [
                "4",
                "C"
              ]
            },
            {
              "text": "13,000",
              "from_grid": [
                "4",
                "C"
              ],
              "to_grid": [
                "4",
                "D"
              ]
            }
          ],
          "annotations_ko": [
            "1. LEVEL 기준\nGL±0=EL+94.00\n1FL±0=EL+94.20\n2FL+6,000=1FL+5,500=EL+99.70\nRFL+10,500=1FL+10,000=EL+104.20",
            "2. 각종 패드, 슬리브, 트렌치, 오프닝은 관련도면을 참조하여 상세도 작성 후 감독관의 승인을 득한 후 시공할 것",
            "3. 도면상 서로 상이한 내용은 발주처 및 설계자와 협의하여 시공할 것",
            "4. 외벽 마감재(창호 포함)의 색상 및 세부 디테일에 대하여는 시방서를 기준하여 SHOP.DWG 및 SAMPLE을 제출하여 감독관 및 발주처의 승인 후 시공할 것",
            "5. PIPE RACK관련 LEVEL 및 상세는 상세도면 및 감독관과 협의 후 시공할 것",
            "6. 내화구조 성능기준\n-기둥, 보, 바닥 : 1시간\n-지붕 : 0.5시간"
          ],
          "unresolved": []
        }
      ]
    },
    {
      "sheet_id": "arch_p062",
      "sheet_number": "A04.03",
      "source_png": "D:\\_Project\\prototype-도면지식관리-mvp\\dwg\\1) 건축공사\\0. PDF 도면\\_png_dpi400\\arch_p062.png",
      "discipline": "architectural",
      "extraction_source": "D:/_Project/prototype-도면지식관리-mvp/docs/ai-3d-builder/outputs/consensus/consensus_p062.json",
      "global_confidence": 0.9,
      "views": [
        {
          "view_id": "v1",
          "view_label": "지상2층 확대평면도",
          "view_scale": "1:200",
          "level": {
            "name": "지상2층",
            "elevation_mm": 99700,
            "ceiling_height_mm": 3000
          },
          "grid": {
            "x_labels": [
              "5",
              "5B",
              "6",
              "7"
            ],
            "y_labels": [
              "A",
              "B",
              "B1",
              "B2",
              "C",
              "D"
            ],
            "x_spacings_mm": [
              8125,
              2875,
              10000
            ],
            "y_spacings_mm": [
              13000,
              6950,
              4100,
              null,
              5950,
              13000
            ],
            "x_direction": "left_to_right",
            "y_direction": "top_to_bottom"
          },
          "grid_validation": {
            "x_spacings_sum_mm": 21000,
            "y_spacings_sum_mm": 43000,
            "x_labels_count": 4,
            "y_labels_count": 6,
            "x_spacings_count": 3,
            "y_spacings_count": 6,
            "x_labels_vs_spacings_ok": true,
            "y_labels_vs_spacings_ok": false
          },
          "anchored_counts": {
            "rooms": {
              "total": 18,
              "anchored": 8,
              "pct": 44.4
            },
            "walls": {
              "total": 6,
              "anchored": 6,
              "pct": 100.0
            },
            "cores": {
              "total": 5,
              "anchored": 1,
              "pct": 20.0
            },
            "voids": {
              "total": 1
            },
            "doors": {
              "total": 0
            },
            "columns": {
              "total": 12
            },
            "dims": {
              "total": 65,
              "anchored": 20,
              "pct": 30.8
            }
          },
          "elements": [
            {
              "id": "r1",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "B"
                ],
                [
                  "5B",
                  "B"
                ],
                [
                  "5B",
                  "B1"
                ],
                [
                  "5",
                  "B1"
                ]
              ],
              "name": "Software Lab",
              "room_number": "L/214",
              "ceiling_height_mm": 3000,
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r2",
              "type": "room",
              "polygon_grid": [
                [
                  "5B",
                  "B"
                ],
                [
                  "6",
                  "B"
                ],
                [
                  "6",
                  "B1"
                ],
                [
                  "5B",
                  "B1"
                ]
              ],
              "name": "휴게공간",
              "room_number": "215",
              "ceiling_height_mm": 3000,
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r3",
              "type": "room",
              "polygon_grid": [
                [
                  "5B",
                  "B1"
                ],
                [
                  "6",
                  "B1"
                ],
                [
                  "6",
                  "B2"
                ],
                [
                  "5B",
                  "B2"
                ]
              ],
              "name": "중회의실",
              "room_number": "M/217",
              "ceiling_height_mm": 3000,
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r4",
              "type": "room",
              "polygon_grid": [
                [
                  "6",
                  "B1"
                ],
                [
                  "7",
                  "B1"
                ],
                [
                  "7",
                  "B2"
                ],
                [
                  "6",
                  "B2"
                ]
              ],
              "name": "OA/탕비실",
              "room_number": "216",
              "ceiling_height_mm": 3000,
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r5",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "B2"
                ],
                [
                  "5B",
                  "B2"
                ],
                [
                  "5B",
                  "C"
                ],
                [
                  "5",
                  "C"
                ]
              ],
              "name": "여자화장실",
              "room_number": "213",
              "ceiling_height_mm": 2700,
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r6",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "C"
                ],
                [
                  "5B",
                  "C"
                ]
              ],
              "name": "중층 조망공간",
              "elevation_mm": 2200,
              "area_m2": null,
              "confidence": 0.6
            },
            {
              "id": "r7",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "C"
                ],
                [
                  "5B",
                  "C"
                ]
              ],
              "name": "남자화장실",
              "room_number": "212",
              "ceiling_height_mm": 2700,
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r8",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "C"
                ],
                [
                  "5B",
                  "C"
                ],
                [
                  "5B",
                  "D"
                ],
                [
                  "5",
                  "D"
                ]
              ],
              "name": "자료실",
              "room_number": "211",
              "ceiling_height_mm": 3000,
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r9",
              "type": "room",
              "polygon_grid": [
                [
                  "5B",
                  "B2"
                ],
                [
                  "6",
                  "B2"
                ],
                [
                  "6",
                  "C"
                ],
                [
                  "5B",
                  "C"
                ]
              ],
              "name": "복도",
              "room_number": "201",
              "ceiling_height_mm": 3000,
              "area_m2": null,
              "confidence": 0.6
            },
            {
              "id": "r10",
              "type": "room",
              "polygon_grid": [
                [
                  "5B",
                  "C"
                ],
                [
                  "6",
                  "C"
                ]
              ],
              "name": "검증시스템 컨트롤실",
              "room_number": "N/210",
              "ceiling_height_mm": 3000,
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r11",
              "type": "room",
              "polygon_grid": [
                [
                  "6",
                  "B2"
                ],
                [
                  "7",
                  "B2"
                ],
                [
                  "7",
                  "C"
                ],
                [
                  "6",
                  "C"
                ]
              ],
              "name": "사무실",
              "room_number": "J/202",
              "ceiling_height_mm": 3000,
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r12",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "D"
                ],
                [
                  "6",
                  "D"
                ]
              ],
              "name": "세미나/다목적실",
              "room_number": "209",
              "ceiling_height_mm": 3000,
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r13",
              "type": "room",
              "polygon_grid": [
                [
                  "6",
                  "D"
                ]
              ],
              "name": "소회의실-1",
              "room_number": "204",
              "ceiling_height_mm": 3000,
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r14",
              "type": "room",
              "polygon_grid": [
                [
                  "6",
                  "D"
                ]
              ],
              "name": "소회의실-2",
              "room_number": "M/205",
              "ceiling_height_mm": 3000,
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r15",
              "type": "room",
              "polygon_grid": [
                [
                  "6",
                  "D"
                ],
                [
                  "7",
                  "D"
                ]
              ],
              "name": "센터장실",
              "room_number": "203",
              "ceiling_height_mm": 3000,
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r16",
              "type": "room",
              "polygon_grid": [
                [
                  "5B",
                  "C"
                ]
              ],
              "name": "PS",
              "confidence": 0.5
            },
            {
              "id": "r17",
              "type": "room",
              "polygon_grid": [
                [
                  "5B",
                  "C"
                ]
              ],
              "name": "EPS/TPS",
              "confidence": 0.5
            },
            {
              "id": "r8",
              "type": "room",
              "polygon_grid": null,
              "name": "검증시스템 컨트롤룸",
              "area_m2": null,
              "confidence": 0.9
            },
            {
              "id": "s1",
              "type": "stair",
              "polygon_grid": [
                [
                  "5",
                  "B1"
                ],
                [
                  "5B",
                  "B1"
                ],
                [
                  "5B",
                  "B2"
                ],
                [
                  "5",
                  "B2"
                ]
              ],
              "label": "계단",
              "confidence": 0.7
            },
            {
              "id": "v1",
              "type": "void",
              "polygon_grid": [
                [
                  "5",
                  "A"
                ],
                [
                  "7",
                  "A"
                ],
                [
                  "7",
                  "B"
                ],
                [
                  "5",
                  "B"
                ]
              ],
              "label": "보이드(吹抜)",
              "confidence": 0.6
            },
            {
              "id": "w_a",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "A"
                ],
                [
                  "7",
                  "A"
                ]
              ],
              "thickness_mm": 200,
              "confidence": 0.6
            },
            {
              "id": "w_d",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "D"
                ],
                [
                  "7",
                  "D"
                ]
              ],
              "thickness_mm": 200,
              "confidence": 0.6
            },
            {
              "id": "w_5",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "A"
                ],
                [
                  "5",
                  "D"
                ]
              ],
              "thickness_mm": 200,
              "confidence": 0.6
            },
            {
              "id": "w_7",
              "type": "wall",
              "path_grid": [
                [
                  "7",
                  "A"
                ],
                [
                  "7",
                  "D"
                ]
              ],
              "thickness_mm": 200,
              "confidence": 0.6
            },
            {
              "id": "w3",
              "type": "wall",
              "path_grid": [
                [
                  "7",
                  "D"
                ],
                [
                  "5",
                  "D"
                ]
              ],
              "thickness_mm": null,
              "label": "외벽",
              "confidence": 0.9
            },
            {
              "id": "w4",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "D"
                ],
                [
                  "5",
                  "A"
                ]
              ],
              "thickness_mm": null,
              "label": "외벽",
              "confidence": 0.9
            },
            {
              "id": "c1",
              "type": "column",
              "at_grid": [
                "5",
                "A"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c2",
              "type": "column",
              "at_grid": [
                "6",
                "A"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c3",
              "type": "column",
              "at_grid": [
                "7",
                "A"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c4",
              "type": "column",
              "at_grid": [
                "5",
                "B"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c5",
              "type": "column",
              "at_grid": [
                "6",
                "B"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c6",
              "type": "column",
              "at_grid": [
                "7",
                "B"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c7",
              "type": "column",
              "at_grid": [
                "5",
                "C"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c8",
              "type": "column",
              "at_grid": [
                "6",
                "C"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c9",
              "type": "column",
              "at_grid": [
                "7",
                "C"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c10",
              "type": "column",
              "at_grid": [
                "5",
                "D"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c11",
              "type": "column",
              "at_grid": [
                "6",
                "D"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c12",
              "type": "column",
              "at_grid": [
                "7",
                "D"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "st1",
              "type": "stair",
              "on_wall_from": null,
              "on_wall_to": null,
              "offset_from_first_mm": null,
              "width_mm": null,
              "label": "계단실",
              "confidence": 0.9
            },
            {
              "id": "ev1",
              "type": "elevator",
              "at_grid": null,
              "size_mm": null,
              "label": "EV",
              "confidence": 0.9
            },
            {
              "id": "sh1",
              "type": "shaft",
              "at_grid": null,
              "size_mm": null,
              "label": "PS",
              "confidence": 0.8
            },
            {
              "id": "sh2",
              "type": "shaft",
              "at_grid": null,
              "size_mm": null,
              "label": "EPS/TPS",
              "confidence": 0.8
            }
          ],
          "dimensions_raw": [
            {
              "text": "21000",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "7",
                "A"
              ]
            },
            {
              "text": "8125",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "5B",
                "A"
              ]
            },
            {
              "text": "2875",
              "from_grid": [
                "5B",
                "A"
              ],
              "to_grid": [
                "6",
                "A"
              ]
            },
            {
              "text": "10000",
              "from_grid": [
                "6",
                "A"
              ],
              "to_grid": [
                "7",
                "A"
              ]
            },
            {
              "text": "5500",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "5000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "735",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "43000",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "5",
                "D"
              ]
            },
            {
              "text": "13000",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "5",
                "B"
              ]
            },
            {
              "text": "6950",
              "from_grid": [
                "5",
                "B"
              ],
              "to_grid": [
                "5",
                "B1"
              ]
            },
            {
              "text": "4100",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5",
                "B2"
              ]
            },
            {
              "text": "5950",
              "from_grid": [
                "5",
                "B2"
              ],
              "to_grid": [
                "5",
                "C"
              ]
            },
            {
              "text": "13000",
              "from_grid": [
                "5",
                "C"
              ],
              "to_grid": [
                "5",
                "D"
              ]
            },
            {
              "text": "4500",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "4000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2700",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "15550",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "20465",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "9000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "8200",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "6400",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "13030",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "4735",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "21,000",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "7",
                "A"
              ]
            },
            {
              "text": "8,125",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "5B",
                "A"
              ]
            },
            {
              "text": "2,875",
              "from_grid": [
                "5B",
                "A"
              ],
              "to_grid": [
                "6",
                "A"
              ]
            },
            {
              "text": "10,000",
              "from_grid": [
                "6",
                "A"
              ],
              "to_grid": [
                "7",
                "A"
              ]
            },
            {
              "text": "13,000",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "5",
                "B"
              ]
            },
            {
              "text": "6,950",
              "from_grid": [
                "5",
                "B"
              ],
              "to_grid": [
                "5",
                "B1"
              ]
            },
            {
              "text": "4,100",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5",
                "B2"
              ]
            },
            {
              "text": "5,950",
              "from_grid": [
                "5",
                "B2"
              ],
              "to_grid": [
                "5",
                "C"
              ]
            },
            {
              "text": "13,000",
              "from_grid": [
                "5",
                "C"
              ],
              "to_grid": [
                "5",
                "D"
              ]
            },
            {
              "text": "43,000",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "5",
                "D"
              ]
            },
            {
              "text": "5,500",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "5,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "4,500",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "4,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "7,250",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "4,300",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "7,050",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3,685",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "7,595",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3,350",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,150",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,275",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3,400",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,250",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,500",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,400",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,025",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,200",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "675",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,800",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "6,400",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "8,200",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "9,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3,450",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3,550",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "15,550",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "20,465",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "970",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "13,030",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "4,735",
              "from_grid": null,
              "to_grid": null
            }
          ],
          "annotations_ko": [
            "Ø150 SST 선홈통",
            "Ø100 SST 횡주관",
            "Ø100 R.D (2EA)",
            "2FL±0 FH+99.70"
          ],
          "unresolved": []
        },
        {
          "view_id": "v2",
          "view_label": "옥탑 확대평면도",
          "view_scale": "1:200",
          "level": {
            "name": "옥탑 (RFL)",
            "elevation_mm": 104200,
            "ceiling_height_mm": null
          },
          "grid": {
            "x_labels": [
              "5",
              "5B",
              "6",
              "7"
            ],
            "y_labels": [
              "A",
              "B",
              "B1",
              "B2",
              "C",
              "D"
            ],
            "x_spacings_mm": [
              8125,
              2875,
              10000
            ],
            "y_spacings_mm": [
              13000,
              6950,
              4100,
              null,
              5950,
              13000
            ],
            "x_direction": "left_to_right",
            "y_direction": "top_to_bottom"
          },
          "grid_validation": {
            "x_spacings_sum_mm": 21000,
            "y_spacings_sum_mm": 43000,
            "x_labels_count": 4,
            "y_labels_count": 6,
            "x_spacings_count": 3,
            "y_spacings_count": 6,
            "x_labels_vs_spacings_ok": true,
            "y_labels_vs_spacings_ok": false
          },
          "anchored_counts": {
            "rooms": {
              "total": 3,
              "anchored": 2,
              "pct": 66.7
            },
            "walls": {
              "total": 6,
              "anchored": 6,
              "pct": 100.0
            },
            "cores": {
              "total": 7,
              "anchored": 4,
              "pct": 57.1
            },
            "voids": {
              "total": 0
            },
            "doors": {
              "total": 0
            },
            "columns": {
              "total": 12
            },
            "dims": {
              "total": 45,
              "anchored": 20,
              "pct": 44.4
            }
          },
          "elements": [
            {
              "id": "rf1",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "A"
                ],
                [
                  "7",
                  "A"
                ],
                [
                  "7",
                  "B"
                ],
                [
                  "5",
                  "B"
                ]
              ],
              "name": "지붕(상부 기계 공간)",
              "label": "RSFL+1,800 FH+106.00",
              "confidence": 0.6
            },
            {
              "id": "rf2",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "B1"
                ],
                [
                  "6",
                  "B1"
                ],
                [
                  "6",
                  "B2"
                ],
                [
                  "5",
                  "B2"
                ]
              ],
              "name": "계단실",
              "room_number": "T01",
              "confidence": 0.7
            },
            {
              "id": "eq1",
              "type": "room",
              "polygon_grid": [
                [
                  "5B",
                  "C"
                ],
                [
                  "6",
                  "C"
                ]
              ],
              "name": "장비패드(H:200)",
              "confidence": 0.6
            },
            {
              "id": "rf3",
              "type": "shaft",
              "at_grid": [
                "6",
                "B2"
              ],
              "label": "PS (T03)",
              "confidence": 0.6
            },
            {
              "id": "rf4",
              "type": "shaft",
              "at_grid": [
                "6",
                "C"
              ],
              "label": "EPS/TPS (T02)",
              "confidence": 0.6
            },
            {
              "id": "cl1",
              "type": "stair",
              "polygon_grid": [
                [
                  "7",
                  "B"
                ]
              ],
              "label": "CAGED LADDER",
              "confidence": 0.5
            },
            {
              "id": "cl2",
              "type": "stair",
              "polygon_grid": [
                [
                  "5",
                  "B1"
                ]
              ],
              "label": "CAGED LADDER",
              "confidence": 0.5
            },
            {
              "id": "w_a",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "A"
                ],
                [
                  "7",
                  "A"
                ]
              ],
              "thickness_mm": 200,
              "confidence": 0.6
            },
            {
              "id": "w_d",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "D"
                ],
                [
                  "7",
                  "D"
                ]
              ],
              "thickness_mm": 200,
              "confidence": 0.6
            },
            {
              "id": "w_5",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "A"
                ],
                [
                  "5",
                  "D"
                ]
              ],
              "thickness_mm": 200,
              "confidence": 0.6
            },
            {
              "id": "w_7",
              "type": "wall",
              "path_grid": [
                [
                  "7",
                  "A"
                ],
                [
                  "7",
                  "D"
                ]
              ],
              "thickness_mm": 200,
              "confidence": 0.6
            },
            {
              "id": "w7",
              "type": "wall",
              "path_grid": [
                [
                  "7",
                  "D"
                ],
                [
                  "5",
                  "D"
                ]
              ],
              "thickness_mm": null,
              "label": "파라펫",
              "confidence": 0.9
            },
            {
              "id": "w8",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "D"
                ],
                [
                  "5",
                  "A"
                ]
              ],
              "thickness_mm": null,
              "label": "파라펫",
              "confidence": 0.9
            },
            {
              "id": "c13",
              "type": "column",
              "at_grid": [
                "5",
                "A"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c14",
              "type": "column",
              "at_grid": [
                "6",
                "A"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c15",
              "type": "column",
              "at_grid": [
                "7",
                "A"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c16",
              "type": "column",
              "at_grid": [
                "5",
                "B"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c17",
              "type": "column",
              "at_grid": [
                "6",
                "B"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c18",
              "type": "column",
              "at_grid": [
                "7",
                "B"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c19",
              "type": "column",
              "at_grid": [
                "5",
                "C"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c20",
              "type": "column",
              "at_grid": [
                "6",
                "C"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c21",
              "type": "column",
              "at_grid": [
                "7",
                "C"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c22",
              "type": "column",
              "at_grid": [
                "5",
                "D"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c23",
              "type": "column",
              "at_grid": [
                "6",
                "D"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "c24",
              "type": "column",
              "at_grid": [
                "7",
                "D"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "st2",
              "type": "stair",
              "on_wall_from": null,
              "on_wall_to": null,
              "offset_from_first_mm": null,
              "width_mm": null,
              "label": "계단실",
              "confidence": 0.9
            },
            {
              "id": "sh3",
              "type": "shaft",
              "at_grid": null,
              "size_mm": null,
              "label": "PS",
              "confidence": 0.8
            },
            {
              "id": "sh4",
              "type": "shaft",
              "at_grid": null,
              "size_mm": null,
              "label": "EPS/TPS",
              "confidence": 0.8
            },
            {
              "id": "o1",
              "type": "opening",
              "on_wall_from": null,
              "on_wall_to": null,
              "offset_from_first_mm": null,
              "width_mm": null,
              "label": "오픈트렌치",
              "confidence": 0.8
            }
          ],
          "dimensions_raw": [
            {
              "text": "21000",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "7",
                "A"
              ]
            },
            {
              "text": "8125",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "5B",
                "A"
              ]
            },
            {
              "text": "2875",
              "from_grid": [
                "5B",
                "A"
              ],
              "to_grid": [
                "6",
                "A"
              ]
            },
            {
              "text": "10000",
              "from_grid": [
                "6",
                "A"
              ],
              "to_grid": [
                "7",
                "A"
              ]
            },
            {
              "text": "13000",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "5",
                "B"
              ]
            },
            {
              "text": "6950",
              "from_grid": [
                "5",
                "B"
              ],
              "to_grid": [
                "5",
                "B1"
              ]
            },
            {
              "text": "4100",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5",
                "B2"
              ]
            },
            {
              "text": "5950",
              "from_grid": [
                "5",
                "B2"
              ],
              "to_grid": [
                "5",
                "C"
              ]
            },
            {
              "text": "13000",
              "from_grid": [
                "5",
                "C"
              ],
              "to_grid": [
                "5",
                "D"
              ]
            },
            {
              "text": "43000",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "5",
                "D"
              ]
            },
            {
              "text": "6000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3800",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1200",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2120",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "4885",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "4800",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2800",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "9080",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1920",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "580",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "21,000",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "7",
                "A"
              ]
            },
            {
              "text": "8,125",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "5B",
                "A"
              ]
            },
            {
              "text": "2,875",
              "from_grid": [
                "5B",
                "A"
              ],
              "to_grid": [
                "6",
                "A"
              ]
            },
            {
              "text": "10,000",
              "from_grid": [
                "6",
                "A"
              ],
              "to_grid": [
                "7",
                "A"
              ]
            },
            {
              "text": "13,000",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "5",
                "B"
              ]
            },
            {
              "text": "6,950",
              "from_grid": [
                "5",
                "B"
              ],
              "to_grid": [
                "5",
                "B1"
              ]
            },
            {
              "text": "4,100",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5",
                "B2"
              ]
            },
            {
              "text": "5,950",
              "from_grid": [
                "5",
                "B2"
              ],
              "to_grid": [
                "5",
                "C"
              ]
            },
            {
              "text": "13,000",
              "from_grid": [
                "5",
                "C"
              ],
              "to_grid": [
                "5",
                "D"
              ]
            },
            {
              "text": "43,000",
              "from_grid": [
                "5",
                "A"
              ],
              "to_grid": [
                "5",
                "D"
              ]
            },
            {
              "text": "6,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3,800",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,200",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,270",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3,180",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,120",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "4,385",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,800",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "4,800",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,920",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "9,080",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,400",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,540",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3,020",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,860",
              "from_grid": null,
              "to_grid": null
            }
          ],
          "annotations_ko": [
            "EXPANSION JOINT @6,000x6,000",
            "CONTROL JOINT @6,000x6,000",
            "SLOPE",
            "Ø125 R.D (3EA)",
            "오픈트렌치 (W=300)",
            "CAGED LADDER",
            "장비패드(H:200)",
            "RSFL+1,800 FH+106.00",
            "RFSL=FL+10,000 FH+104.20",
            "RSFL+200 FH+104.40",
            "RFL+200 FH+104.50",
            "RFL±0 FH+104.20",
            "RFL±0 FH+104.30",
            "LEVEL 기준: GL±0=EL+94.00, 1FL±0=EL+94.20, 2FL±0=1FL+5,500=EL+99.70, RFL±0=1FL+10,000=EL+104.20",
            "내화구조 성능기준: 기둥·보·바닥 1시간, 지붕 0.5시간",
            "Ø150 R.D (3EA)"
          ],
          "unresolved": []
        }
      ]
    },
    {
      "sheet_id": "arch_p063",
      "sheet_number": "A05.01",
      "source_png": "D:\\_Project\\prototype-도면지식관리-mvp\\dwg\\1) 건축공사\\0. PDF 도면\\_png_dpi400\\arch_p063.png",
      "discipline": "architectural",
      "extraction_source": "D:/_Project/prototype-도면지식관리-mvp/docs/ai-3d-builder/outputs/2026-04-22_084339_arch_p063_gemini-3.1-flash-image_agent/stage-10-parsed.json",
      "global_confidence": 0.8,
      "views": [
        {
          "view_id": "v1",
          "view_label": "옥탑지붕 계단실 확대평면도",
          "view_scale": "1/100(A3)",
          "level": {
            "name": "옥탑지붕",
            "elevation_mm": null,
            "ceiling_height_mm": null
          },
          "grid": {
            "x_labels": [
              "5",
              "5B"
            ],
            "y_labels": [
              "B1",
              "B2"
            ],
            "x_spacings_mm": [
              8125
            ],
            "y_spacings_mm": [
              4100
            ],
            "x_direction": "left_to_right",
            "y_direction": "top_to_bottom"
          },
          "grid_validation": {
            "x_spacings_sum_mm": 8125,
            "y_spacings_sum_mm": 4100,
            "x_labels_count": 2,
            "y_labels_count": 2,
            "x_spacings_count": 1,
            "y_spacings_count": 1,
            "x_labels_vs_spacings_ok": true,
            "y_labels_vs_spacings_ok": true
          },
          "anchored_counts": {
            "rooms": {
              "total": 1,
              "anchored": 1,
              "pct": 100.0
            },
            "walls": {
              "total": 4,
              "anchored": 4,
              "pct": 100.0
            },
            "cores": {
              "total": 0,
              "anchored": 0,
              "pct": 0.0
            },
            "voids": {
              "total": 0
            },
            "doors": {
              "total": 0
            },
            "columns": {
              "total": 0
            },
            "dims": {
              "total": 10,
              "anchored": 2,
              "pct": 20.0
            }
          },
          "elements": [
            {
              "id": "v1_w1",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "B1"
                ],
                [
                  "5B",
                  "B1"
                ]
              ],
              "thickness_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "v1_w2",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "B2"
                ],
                [
                  "5B",
                  "B2"
                ]
              ],
              "thickness_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "v1_w3",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "B1"
                ],
                [
                  "5",
                  "B2"
                ]
              ],
              "thickness_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "v1_w4",
              "type": "wall",
              "path_grid": [
                [
                  "5B",
                  "B1"
                ],
                [
                  "5B",
                  "B2"
                ]
              ],
              "thickness_mm": null,
              "label": null,
              "confidence": 0.8
            },
            {
              "id": "v1_r1",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "B1"
                ],
                [
                  "5B",
                  "B1"
                ],
                [
                  "5B",
                  "B2"
                ],
                [
                  "5",
                  "B2"
                ]
              ],
              "name": "옥탑지붕 계단실",
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "v1_o1",
              "type": "opening",
              "on_wall_from": [
                "5",
                "B1"
              ],
              "on_wall_to": [
                "5B",
                "B1"
              ],
              "offset_from_first_mm": 1500,
              "width_mm": 1500,
              "label": "패널 캐노피(TYP.)",
              "confidence": 0.6
            }
          ],
          "dimensions_raw": [
            {
              "text": "8,125",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5B",
                "B1"
              ]
            },
            {
              "text": "4,100",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5",
                "B2"
              ]
            },
            {
              "text": "1,500",
              "from_grid": [
                "5B",
                "B1"
              ],
              "to_grid": null
            },
            {
              "text": "150",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "7,925",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "535",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "535",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "3,550",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "535",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "300",
              "from_grid": null,
              "to_grid": null
            }
          ],
          "annotations_ko": [
            "CAGED LADDER",
            "THK236 글라스울 지붕판넬",
            "SLOPE",
            "Ø100 RF DRAIN"
          ],
          "unresolved": []
        },
        {
          "view_id": "v2",
          "view_label": "2층 계단실 확대평면도",
          "view_scale": "1/100(A3)",
          "level": {
            "name": "2층",
            "elevation_mm": null,
            "ceiling_height_mm": null
          },
          "grid": {
            "x_labels": [
              "5",
              "5B"
            ],
            "y_labels": [
              "B1",
              "B2"
            ],
            "x_spacings_mm": [
              8125
            ],
            "y_spacings_mm": [
              4100
            ],
            "x_direction": "left_to_right",
            "y_direction": "top_to_bottom"
          },
          "grid_validation": {
            "x_spacings_sum_mm": 8125,
            "y_spacings_sum_mm": 4100,
            "x_labels_count": 2,
            "y_labels_count": 2,
            "x_spacings_count": 1,
            "y_spacings_count": 1,
            "x_labels_vs_spacings_ok": true,
            "y_labels_vs_spacings_ok": true
          },
          "anchored_counts": {
            "rooms": {
              "total": 4,
              "anchored": 1,
              "pct": 25.0
            },
            "walls": {
              "total": 0,
              "anchored": 0,
              "pct": 0.0
            },
            "cores": {
              "total": 2,
              "anchored": 0,
              "pct": 0.0
            },
            "voids": {
              "total": 0
            },
            "doors": {
              "total": 1
            },
            "columns": {
              "total": 3
            },
            "dims": {
              "total": 13,
              "anchored": 2,
              "pct": 15.4
            }
          },
          "elements": [
            {
              "id": "v2_c1",
              "type": "column",
              "at_grid": [
                "5",
                "B1"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "v2_c2",
              "type": "column",
              "at_grid": [
                "5B",
                "B1"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "v2_c3",
              "type": "column",
              "at_grid": [
                "5B",
                "B2"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "v2_s1",
              "type": "stair",
              "on_wall_from": [
                "5",
                "B1"
              ],
              "on_wall_to": [
                "5B",
                "B1"
              ],
              "offset_from_first_mm": 1820,
              "width_mm": 1450,
              "label": "UP",
              "confidence": 0.8
            },
            {
              "id": "v2_s2",
              "type": "stair",
              "on_wall_from": [
                "5",
                "B1"
              ],
              "on_wall_to": [
                "5B",
                "B1"
              ],
              "offset_from_first_mm": 1820,
              "width_mm": 1450,
              "label": "DN",
              "confidence": 0.8
            },
            {
              "id": "v2_r1",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "B1"
                ],
                [
                  "5B",
                  "B1"
                ],
                [
                  "5B",
                  "B2"
                ],
                [
                  "5",
                  "B2"
                ]
              ],
              "name": "계단실",
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "v2_r2",
              "type": "room",
              "polygon_grid": null,
              "name": "Software Lab",
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "v2_r3",
              "type": "room",
              "polygon_grid": null,
              "name": "로비",
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "v2_r4",
              "type": "room",
              "polygon_grid": null,
              "name": "여자화장실",
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "v2_d1",
              "type": "door",
              "on_wall_from": [
                "5B",
                "B1"
              ],
              "on_wall_to": [
                "5B",
                "B2"
              ],
              "offset_from_first_mm": null,
              "width_mm": null,
              "label": "양개형 접이식 방화문",
              "confidence": 0.6
            }
          ],
          "dimensions_raw": [
            {
              "text": "8,125",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5B",
                "B1"
              ]
            },
            {
              "text": "7,825",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "4,100",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5",
                "B2"
              ]
            },
            {
              "text": "3,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "550",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "550",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,820",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,665",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,245",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,385",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,450",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,450",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "300",
              "from_grid": null,
              "to_grid": null
            }
          ],
          "annotations_ko": [
            "중층 조망공간",
            "2FL+2,200"
          ],
          "unresolved": []
        },
        {
          "view_id": "v3",
          "view_label": "옥탑층 계단실 확대평면도",
          "view_scale": "1/100(A3)",
          "level": {
            "name": "옥탑층",
            "elevation_mm": null,
            "ceiling_height_mm": null
          },
          "grid": {
            "x_labels": [
              "5",
              "5B"
            ],
            "y_labels": [
              "B1",
              "B2"
            ],
            "x_spacings_mm": [
              8125
            ],
            "y_spacings_mm": [
              4100
            ],
            "x_direction": "left_to_right",
            "y_direction": "top_to_bottom"
          },
          "grid_validation": {
            "x_spacings_sum_mm": 8125,
            "y_spacings_sum_mm": 4100,
            "x_labels_count": 2,
            "y_labels_count": 2,
            "x_spacings_count": 1,
            "y_spacings_count": 1,
            "x_labels_vs_spacings_ok": true,
            "y_labels_vs_spacings_ok": true
          },
          "anchored_counts": {
            "rooms": {
              "total": 1,
              "anchored": 1,
              "pct": 100.0
            },
            "walls": {
              "total": 0,
              "anchored": 0,
              "pct": 0.0
            },
            "cores": {
              "total": 1,
              "anchored": 0,
              "pct": 0.0
            },
            "voids": {
              "total": 0
            },
            "doors": {
              "total": 0
            },
            "columns": {
              "total": 4
            },
            "dims": {
              "total": 14,
              "anchored": 2,
              "pct": 14.3
            }
          },
          "elements": [
            {
              "id": "v3_c1",
              "type": "column",
              "at_grid": [
                "5",
                "B1"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "v3_c2",
              "type": "column",
              "at_grid": [
                "5B",
                "B1"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "v3_c3",
              "type": "column",
              "at_grid": [
                "5B",
                "B2"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "v3_c4",
              "type": "column",
              "at_grid": [
                "5",
                "B2"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "v3_s1",
              "type": "stair",
              "on_wall_from": [
                "5",
                "B1"
              ],
              "on_wall_to": [
                "5B",
                "B1"
              ],
              "offset_from_first_mm": 1545,
              "width_mm": 1450,
              "label": "DN",
              "confidence": 0.8
            },
            {
              "id": "v3_r1",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "B1"
                ],
                [
                  "5B",
                  "B1"
                ],
                [
                  "5B",
                  "B2"
                ],
                [
                  "5",
                  "B2"
                ]
              ],
              "name": "계단실",
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "v3_o1",
              "type": "opening",
              "on_wall_from": [
                "5",
                "B1"
              ],
              "on_wall_to": [
                "5B",
                "B1"
              ],
              "offset_from_first_mm": 1500,
              "width_mm": 1500,
              "label": "상부 패널 캐노피(TYP.)",
              "confidence": 0.6
            }
          ],
          "dimensions_raw": [
            {
              "text": "8,125",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5B",
                "B1"
              ]
            },
            {
              "text": "7,675",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "4,100",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5",
                "B2"
              ]
            },
            {
              "text": "3,000",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "550",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "550",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,545",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,445",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,500",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,255",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,945",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,450",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,450",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "300",
              "from_grid": null,
              "to_grid": null
            }
          ],
          "annotations_ko": [
            "CAGED LADDER",
            "FL±0"
          ],
          "unresolved": []
        },
        {
          "view_id": "v4",
          "view_label": "1층 계단실 확대평면도",
          "view_scale": "1/100(A3)",
          "level": {
            "name": "1층",
            "elevation_mm": null,
            "ceiling_height_mm": null
          },
          "grid": {
            "x_labels": [
              "5",
              "5A",
              "5B"
            ],
            "y_labels": [
              "B1",
              "B2"
            ],
            "x_spacings_mm": [
              2000,
              6125
            ],
            "y_spacings_mm": [
              4100
            ],
            "x_direction": "left_to_right",
            "y_direction": "top_to_bottom"
          },
          "grid_validation": {
            "x_spacings_sum_mm": 8125,
            "y_spacings_sum_mm": 4100,
            "x_labels_count": 3,
            "y_labels_count": 2,
            "x_spacings_count": 2,
            "y_spacings_count": 1,
            "x_labels_vs_spacings_ok": true,
            "y_labels_vs_spacings_ok": true
          },
          "anchored_counts": {
            "rooms": {
              "total": 4,
              "anchored": 1,
              "pct": 25.0
            },
            "walls": {
              "total": 0,
              "anchored": 0,
              "pct": 0.0
            },
            "cores": {
              "total": 1,
              "anchored": 0,
              "pct": 0.0
            },
            "voids": {
              "total": 0
            },
            "doors": {
              "total": 0
            },
            "columns": {
              "total": 4
            },
            "dims": {
              "total": 15,
              "anchored": 4,
              "pct": 26.7
            }
          },
          "elements": [
            {
              "id": "v4_c1",
              "type": "column",
              "at_grid": [
                "5",
                "B1"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "v4_c2",
              "type": "column",
              "at_grid": [
                "5B",
                "B1"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "v4_c3",
              "type": "column",
              "at_grid": [
                "5B",
                "B2"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "v4_c4",
              "type": "column",
              "at_grid": [
                "5",
                "B2"
              ],
              "size_mm": null,
              "label": null,
              "confidence": 0.7
            },
            {
              "id": "v4_s1",
              "type": "stair",
              "on_wall_from": [
                "5",
                "B1"
              ],
              "on_wall_to": [
                "5B",
                "B1"
              ],
              "offset_from_first_mm": 1820,
              "width_mm": 1500,
              "label": "UP",
              "confidence": 0.8
            },
            {
              "id": "v4_r1",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "B1"
                ],
                [
                  "5B",
                  "B1"
                ],
                [
                  "5B",
                  "B2"
                ],
                [
                  "5",
                  "B2"
                ]
              ],
              "name": "계단실",
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "v4_r2",
              "type": "room",
              "polygon_grid": null,
              "name": "장애인화장실(여)",
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "v4_r3",
              "type": "room",
              "polygon_grid": null,
              "name": "장애인화장실(남)",
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "v4_r4",
              "type": "room",
              "polygon_grid": null,
              "name": "로비",
              "area_m2": null,
              "confidence": 0.7
            }
          ],
          "dimensions_raw": [
            {
              "text": "8,125",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5B",
                "B1"
              ]
            },
            {
              "text": "2,000",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5A",
                "B1"
              ]
            },
            {
              "text": "6,125",
              "from_grid": [
                "5A",
                "B1"
              ],
              "to_grid": [
                "5B",
                "B1"
              ]
            },
            {
              "text": "4,100",
              "from_grid": [
                "5",
                "B1"
              ],
              "to_grid": [
                "5",
                "B2"
              ]
            },
            {
              "text": "1,650",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "2,050",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "400",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "400",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,600",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "4,300",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,825",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,820",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,825",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "1,500",
              "from_grid": null,
              "to_grid": null
            },
            {
              "text": "300",
              "from_grid": null,
              "to_grid": null
            }
          ],
          "annotations_ko": [],
          "unresolved": []
        }
      ]
    },
    {
      "sheet_id": "arch_p064",
      "sheet_number": "A05.02",
      "source_png": "D:\\_Project\\prototype-도면지식관리-mvp\\dwg\\1) 건축공사\\0. PDF 도면\\_png_dpi400\\arch_p064.png",
      "discipline": "architectural",
      "extraction_source": "D:/_Project/prototype-도면지식관리-mvp/docs/ai-3d-builder/outputs/2026-04-22_084401_arch_p064_gemini-3.1-flash-image_agent/stage-10-parsed.json",
      "global_confidence": 0.9,
      "views": [
        {
          "view_id": "v1",
          "view_label": "계단실 확대단면도-1",
          "view_scale": "1/100(A3)",
          "level": {
            "name": "복합",
            "elevation_mm": null,
            "ceiling_height_mm": null
          },
          "grid": {
            "x_labels": [
              "5",
              "5B"
            ],
            "y_labels": [
              "T.O.PARTAPET",
              "T.O.S",
              "RF SL±0",
              "2FL±0",
              "1FL±0",
              "PIT FL±0"
            ],
            "x_spacings_mm": [
              8125
            ],
            "y_spacings_mm": [
              700,
              3500,
              4300,
              5500,
              2500
            ],
            "x_direction": "left_to_right",
            "y_direction": "top_to_bottom"
          },
          "grid_validation": {
            "x_spacings_sum_mm": 8125,
            "y_spacings_sum_mm": 16500,
            "x_labels_count": 2,
            "y_labels_count": 6,
            "x_spacings_count": 1,
            "y_spacings_count": 5,
            "x_labels_vs_spacings_ok": true,
            "y_labels_vs_spacings_ok": true
          },
          "anchored_counts": {
            "rooms": {
              "total": 5,
              "anchored": 5,
              "pct": 100.0
            },
            "walls": {
              "total": 2,
              "anchored": 2,
              "pct": 100.0
            },
            "cores": {
              "total": 1,
              "anchored": 0,
              "pct": 0.0
            },
            "voids": {
              "total": 0
            },
            "doors": {
              "total": 0
            },
            "columns": {
              "total": 0
            },
            "dims": {
              "total": 8,
              "anchored": 6,
              "pct": 75.0
            }
          },
          "elements": [
            {
              "id": "w1",
              "type": "wall",
              "path_grid": [
                [
                  "5",
                  "T.O.PARTAPET"
                ],
                [
                  "5",
                  "PIT FL±0"
                ]
              ],
              "thickness_mm": null,
              "label": "THK236 글라스울 지붕판넬 (내화구조 0.5시간)",
              "confidence": 0.8
            },
            {
              "id": "w2",
              "type": "wall",
              "path_grid": [
                [
                  "5B",
                  "T.O.PARTAPET"
                ],
                [
                  "5B",
                  "PIT FL±0"
                ]
              ],
              "thickness_mm": null,
              "label": "THK3 A.L SHEET",
              "confidence": 0.8
            },
            {
              "id": "st1",
              "type": "stair",
              "on_wall_from": [
                "5",
                "1FL±0"
              ],
              "on_wall_to": [
                "5B",
                "RF SL±0"
              ],
              "offset_from_first_mm": null,
              "width_mm": null,
              "label": "계단",
              "confidence": 0.9
            },
            {
              "id": "r1",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "1FL±0"
                ],
                [
                  "5B",
                  "1FL±0"
                ],
                [
                  "5B",
                  "2FL±0"
                ],
                [
                  "5",
                  "2FL±0"
                ]
              ],
              "name": "장애인화장실(여)",
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r2",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "1FL±0"
                ],
                [
                  "5B",
                  "1FL±0"
                ],
                [
                  "5B",
                  "2FL±0"
                ],
                [
                  "5",
                  "2FL±0"
                ]
              ],
              "name": "장애인화장실(남)",
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r3",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "1FL±0"
                ],
                [
                  "5B",
                  "1FL±0"
                ],
                [
                  "5B",
                  "2FL±0"
                ],
                [
                  "5",
                  "2FL±0"
                ]
              ],
              "name": "청소도구실",
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r4",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "2FL±0"
                ],
                [
                  "5B",
                  "2FL±0"
                ],
                [
                  "5B",
                  "RF SL±0"
                ],
                [
                  "5",
                  "RF SL±0"
                ]
              ],
              "name": "복도",
              "area_m2": null,
              "confidence": 0.7
            },
            {
              "id": "r5",
              "type": "room",
              "polygon_grid": [
                [
                  "5",
                  "2FL±0"
                ],
                [
                  "5B",
                  "2FL±0"
                ],
                [
                  "5B",
                  "RF SL±0"
                ],
                [
                  "5",
                  "RF SL±0"
                ]
              ],
              "name": "로비",
              "area_m2": null,
              "confidence": 0.7
            }
          ],
          "dimensions_raw": [
            {
              "text": "8,125",
              "from_grid": [
                "5",
                "T.O.PARTAPET"
              ],
              "to_grid": [
                "5B",
                "T.O.PARTAPET"
              ]
            },
            {
              "text": "6,700",
              "from_grid": [
                "5",
                "T.O.PARTAPET"
              ],
              "to_grid": null
            },
            {
              "text": "1,425",
              "from_grid": null,
              "to_grid": [
                "5B",
                "T.O.PARTAPET"
              ]
            },
            {
              "text": "700",
              "from_grid": [
                "5",
                "T.O.PARTAPET"
              ],
              "to_grid": [
                "5",
                "T.O.S"
              ]
            },
            {
              "text": "3,500",
              "from_grid": [
                "5",
                "T.O.S"
              ],
              "to_grid": [
                "5",
                "RF SL±0"
              ]
            },
            {
              "text": "4,300",
              "from_grid": [
                "5",
                "RF SL±0"
              ],
              "to_grid": [
                "5",
                "2FL±0"
              ]
            },
            {
              "text": "5,500",
              "from_grid": [
                "5",
                "2FL±0"
              ],
              "to_grid": [
                "5",
                "1FL±0"
              ]
            },
            {
              "text": "2,500",
              "from_grid": [
                "5",
                "1FL±0"
              ],
              "to_grid": [
                "5",
                "PIT FL±0"
              ]
            }
          ],
          "annotations_ko": [
            "THK236 글라스울 지붕판넬 (내화구조 0.5시간)",
            "THK3 A.L SHEET",
            "THK135 글라스울 판넬",
            "THK100 무근콘크리트 기계미장 (#8 W.M 150X150)",
            "THK0.1 PE필름 1겹",
            "THK10 방수층보호재",
            "고무아스팔트 복합방수",
            "THK200 압출법 보온판(특호)",
            "THK125 글라스울 판넬 (내화 1시간)",
            "양개형 접이식 방화문",
            "THK3 PVC 타일",
            "THK27 시멘트몰탈",
            "THK12 강화유리",
            "THK123 글라스울 판넬 (내화 1시간)",
            "THK150 압출법 보온판(특호)",
            "침투식 방수",
            "THK60 버림 콘크리트",
            "THK0.1 PE 필름 2겹"
          ],
          "unresolved": []
        },
        {
          "view_id": "v2",
          "view_label": "계단실 확대단면도-2",
          "view_scale": "1/100(A3)",
          "level": {
            "name": "복합",
            "elevation_mm": null,
            "ceiling_height_mm": null
          },
          "grid": {
            "x_labels": [
              "B2",
              "B1"
            ],
            "y_labels": [
              "T.O.PARTAPET",
              "T.O.S",
              "RF SL±0"
            ],
            "x_spacings_mm": [
              4100
            ],
            "y_spacings_mm": [
              700,
              3500
            ],
            "x_direction": "left_to_right",
            "y_direction": "top_to_bottom"
          },
          "grid_validation": {
            "x_spacings_sum_mm": 4100,
            "y_spacings_sum_mm": 4200,
            "x_labels_count": 2,
            "y_labels_count": 3,
            "x_spacings_count": 1,
            "y_spacings_count": 2,
            "x_labels_vs_spacings_ok": true,
            "y_labels_vs_spacings_ok": true
          },
          "anchored_counts": {
            "rooms": {
              "total": 1,
              "anchored": 1,
              "pct": 100.0
            },
            "walls": {
              "total": 2,
              "anchored": 2,
              "pct": 100.0
            },
            "cores": {
              "total": 0,
              "anchored": 0,
              "pct": 0.0
            },
            "voids": {
              "total": 0
            },
            "doors": {
              "total": 0
            },
            "columns": {
              "total": 0
            },
            "dims": {
              "total": 4,
              "anchored": 4,
              "pct": 100.0
            }
          },
          "elements": [
            {
              "id": "w3",
              "type": "wall",
              "path_grid": [
                [
                  "B2",
                  "T.O.PARTAPET"
                ],
                [
                  "B2",
                  "RF SL±0"
                ]
              ],
              "thickness_mm": null,
              "label": "THK135 글라스울 판넬",
              "confidence": 0.8
            },
            {
              "id": "w4",
              "type": "wall",
              "path_grid": [
                [
                  "B1",
                  "T.O.PARTAPET"
                ],
                [
                  "B1",
                  "RF SL±0"
                ]
              ],
              "thickness_mm": null,
              "label": "THK3 A.L SHEET",
              "confidence": 0.8
            },
            {
              "id": "r6",
              "type": "room",
              "polygon_grid": [
                [
                  "B2",
                  "T.O.S"
                ],
                [
                  "B1",
                  "T.O.S"
                ],
                [
                  "B1",
                  "RF SL±0"
                ],
                [
                  "B2",
                  "RF SL±0"
                ]
              ],
              "name": "계단실",
              "area_m2": null,
              "confidence": 0.7
            }
          ],
          "dimensions_raw": [
            {
              "text": "4,100",
              "from_grid": [
                "B2",
                "T.O.PARTAPET"
              ],
              "to_grid": [
                "B1",
                "T.O.PARTAPET"
              ]
            },
            {
              "text": "4,100",
              "from_grid": [
                "B2",
                "T.O.PARTAPET"
              ],
              "to_grid": [
                "B1",
                "T.O.PARTAPET"
              ]
            },
            {
              "text": "700",
              "from_grid": [
                "B2",
                "T.O.PARTAPET"
              ],
              "to_grid": [
                "B2",
                "T.O.S"
              ]
            },
            {
              "text": "3,500",
              "from_grid": [
                "B2",
                "T.O.S"
              ],
              "to_grid": [
                "B2",
                "RF SL±0"
              ]
            }
          ],
          "annotations_ko": [
            "Ø100 R.D(2EA) 거터 (300X250)",
            "THK236 글라스울 지붕판넬 (내화구조 0.5시간)",
            "THK3 A.L SHEET",
            "THK135 글라스울 판넬",
            "THK100 무근콘크리트 기계미장 (#8 W.M 150X150)",
            "THK0.1 PE필름 1겹",
            "THK10 방수층보호재",
            "고무아스팔트 복합방수"
          ],
          "unresolved": []
        }
      ]
    }
  ],
  "level_stack": {
    "levels_mm": {
      "2FL": 99700,
      "RFL": 104200,
      "GL": 94000,
      "1FL": 94200
    },
    "offsets_mm": {
      "RSFL+1800": 106000,
      "RSFL+200": 104400,
      "RFL+200": 104500,
      "1FL+5500": 99700,
      "1FL+10000": 104200
    },
    "ffh_mm": {
      "GL→1FL": 200,
      "1FL→2FL": 5500,
      "2FL→RFL": 4500
    }
  }
};
