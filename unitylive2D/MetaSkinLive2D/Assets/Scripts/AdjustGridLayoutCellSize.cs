using UnityEngine;
using UnityEngine.UI;
 
[ExecuteInEditMode]
[RequireComponent(typeof(GridLayoutGroup))]

// from: https://forum.unity.com/threads/solved-how-to-make-grid-layout-group-cell-size-x-auto-expand.448534/
public class AdjustGridLayoutCellSize : MonoBehaviour
{
    public enum Axis { X, Y };
    public enum RatioMode { Free, Fixed };
 
    [SerializeField] Axis expand;
    [SerializeField] RatioMode ratioMode;
    [SerializeField] float cellRatio = 1;
 
    new RectTransform transform;
    GridLayoutGroup grid;
 
    void Awake()
    {
        transform = (RectTransform)base.transform;
        grid = GetComponent<GridLayoutGroup>();
    }
 
    // Start is called before the first frame update
    void Start()
    {
        UpdateCellSize();
    }
 
    void OnRectTransformDimensionsChange()
    {
        if (grid != null)
            UpdateCellSize();
    }
 
#if UNITY_EDITOR
    [ExecuteAlways]
    void Update()
    {
        UpdateCellSize();
    }
#endif
 
    void OnValidate()
    {
        transform = (RectTransform)base.transform;
        grid = GetComponent<GridLayoutGroup>();
        UpdateCellSize();
    }
 
    void UpdateCellSize()
    {
        var count = grid.constraintCount;
        if (expand == Axis.X)
        {
            float spacing = (count - 1) * grid.spacing.x;
            float contentSize = transform.rect.width - grid.padding.left - grid.padding.right - spacing;
            float sizePerCell = contentSize / count;
            grid.cellSize = new Vector2(sizePerCell, ratioMode == RatioMode.Free ? grid.cellSize.y : sizePerCell * cellRatio);
         
        }
        else //if (expand == Axis.Y)
        {
            float spacing = (count - 1) * grid.spacing.y;
            float contentSize = transform.rect.height - grid.padding.top - grid.padding.bottom -spacing;
            float sizePerCell = contentSize / count;
            grid.cellSize = new Vector2(ratioMode == RatioMode.Free ? grid.cellSize.x : sizePerCell * cellRatio, sizePerCell);
        }
    }
}