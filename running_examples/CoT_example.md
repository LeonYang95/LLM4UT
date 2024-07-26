You are an AI programming assistant, utilizing the DeepSeek Coder model, developed by DeepSeek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.

### Intention Instruction:

Your task is to write some unit tests. Please first understand the intent of the target method, the method you are going to test is at the end of the instruction.
```
// The method belongs to the class:
org.jfree.chart.plot.CategoryPlot

// Constructor:
public CategoryPlot();
public CategoryPlot(CategoryDataset dataset, CategoryAxis domainAxis, ValueAxis rangeAxis, CategoryItemRenderer renderer);

// Fields
private static final long serialVersionUID = -3537691700434728188L;
public static final boolean DEFAULT_DOMAIN_GRIDLINES_VISIBLE = false;
public static final boolean DEFAULT_RANGE_GRIDLINES_VISIBLE = true;
...

// Other methods
public void setRangeAxisLocation(int index, AxisLocation location, boolean notify);
public void addRangeMarker(Marker marker, Layer layer);
public void setAnchorValue(double value, boolean notify);
...

// The following code is the method that you are going to test.
public boolean removeDomainMarker(int index, Marker marker, Layer layer, boolean notify) {
    ArrayList markers;
    if (layer == Layer.FOREGROUND) {
        markers = (ArrayList) this.foregroundDomainMarkers.get(new Integer(index));
    } else {
        markers = (ArrayList) this.backgroundDomainMarkers.get(new Integer(index));
    }
    if (markers == null) {
        return false;
    }
    boolean removed = markers.remove(marker);
    if (removed && notify) {
        fireChangeEvent();
    }
    return removed;
}
```
Please infer the intention of the removeDomainMarker method.

### Intention Response:

The `removeDomainMarker` method is intended to remove a marker from the domain axis of a CategoryPlot. The method takes four parameters: an integer `index`, a `Marker` object, a `Layer` object, and a boolean `notify`.

The `index` parameter is used to specify the domain axis on which the marker is to be removed. The `Marker` object is the marker to be removed. The `Layer` object specifies whether the marker is in the foreground or background layer. The `notify` parameter is a flag indicating whether to notify the plot that a change has occurred.

The method retrieves the list of markers for the specified domain axis and layer from the `foregroundDomainMarkers` or `backgroundDomainMarkers` field, depending on the `Layer` parameter. If the list is null, the method returns false.

If the list is not null, the method attempts to remove the marker from the list. If the marker is successfully removed, the method checks the `notify` parameter. If `notify` is true, it calls the `fireChangeEvent` method to notify the plot that a change has occurred.

The method returns a boolean indicating whether the marker was successfully removed.

This method seems to be part of a plotting library, likely for creating charts, and it's used to manage the markers on the domain axis of the plot.
<|EOT|>

### Generation Instruction:

The `removeDomainMarker` method is intended to remove a marker from the domain axis of a CategoryPlot. The method takes four parameters: an integer `index`, a `Marker` object, a `Layer` object, and a boolean `notify`.

The `index` parameter is used to specify the domain axis on which the marker is to be removed. The `Marker` object is the marker to be removed. The `Layer` object specifies whether the marker is in the foreground or background layer. The `notify` parameter is a flag indicating whether to notify the plot that a change has occurred.

The method retrieves the list of markers for the specified domain axis and layer from the `foregroundDomainMarkers` or `backgroundDomainMarkers` field, depending on the `Layer` parameter. If the list is null, the method returns false.

If the list is not null, the method attempts to remove the marker from the list. If the marker is successfully removed, the method checks the `notify` parameter. If `notify` is true, it calls the `fireChangeEvent` method to notify the plot that a change has occurred.

The method returns a boolean indicating whether the marker was successfully removed.

This method seems to be part of a plotting library, likely for creating charts, and it's used to manage the markers on the domain axis of the plot.

You are a professional who writes Java test methods. Please write some unit tests for the removeDomainMarker method with the given intention. You should write unit tests with maximizing both branch and line coverage.

### Generation Response:
```java
import org.junit.Test;
import org.junit.Assert;
import org.junit.Before;
import org.junit.After; 
import org.junit.Assert.*;
import org.junit.Ignore;
import org.junit.BeforeClass;
import org.junit.AfterClass;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;
import org.junit.Rule;
import org.junit.rules.ExpectedException;
import static org.mockito.Mockito.*;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import java.awt.*;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.util.*;
import org.jfree.chart.LegendItem;
import org.jfree.chart.LegendItemCollection;
import org.jfree.chart.annotations.CategoryAnnotation;
import org.jfree.chart.axis.*;
import org.jfree.chart.event.ChartChangeEventType;
import org.jfree.chart.event.PlotChangeEvent;
import org.jfree.chart.event.RendererChangeEvent;
import org.jfree.chart.event.RendererChangeListener;
import org.jfree.chart.renderer.category.CategoryItemRenderer;
import org.jfree.chart.renderer.category.CategoryItemRendererState;
import org.jfree.chart.util.*;
import org.jfree.data.Range;
import org.jfree.data.category.CategoryDataset;
import org.jfree.data.general.Dataset;
import org.jfree.data.general.DatasetChangeEvent;
import org.jfree.data.general.DatasetUtilities;

public class CategoryPlotTest{

    private CategoryPlot plot;
    private CategoryDataset dataset;
    private CategoryAxis domainAxis;
    private ValueAxis rangeAxis;
    private CategoryItemRenderer renderer;

    @Before
    public void setUp() {
        plot = new CategoryPlot();
        dataset = mock(CategoryDataset.class);
        domainAxis = mock(CategoryAxis.class);
        rangeAxis = mock(ValueAxis.class);
        renderer = mock(CategoryItemRenderer.class);
    }

    @Test
    public void testRemoveDomainMarker_LayerIsForeground_MarkerExists_NotifyTrue() {
        ArrayList<Marker> markers = new ArrayList<>();
        Marker marker = mock(Marker.class);
        markers.add(marker);
        plot.setForegroundDomainMarkers(new HashMap<Integer, ArrayList<Marker>>() {{
            put(0, markers);
        }});

        boolean result = plot.removeDomainMarker(0, marker, Layer.FOREGROUND, true);

        Assert.assertTrue(result);
        Assert.assertEquals(0, plot.getForegroundDomainMarkers().get(0).size());
        verify(plot, times(1)).fireChangeEvent();
    }

    @Test
    public void testRemoveDomainMarker_LayerIsForeground_MarkerExists_NotifyFalse() {
        ArrayList<Marker> markers = new ArrayList<>();
        Marker marker = mock(Marker.class);
        markers.add(marker);
        plot.setForegroundDomainMarkers(new HashMap<Integer, ArrayList<Marker>>() {{
            put(0, markers);
        }});

        boolean result = plot.removeDomainMarker(0, marker, Layer.FOREGROUND, false);

        Assert.assertTrue(result);
        Assert.assertEquals(0, plot.getForegroundDomainMarkers().get(0).size());
        verify(plot, times(0)).fireChangeEvent();
    }

    @Test
    public void testRemoveDomainMarker_LayerIsForeground_MarkerDoesNotExist_ReturnsFalse() {
        ArrayList<Marker> markers = new ArrayList<>();
        Marker marker = mock(Marker.class);
        plot.setForegroundDomainMarkers(new HashMap<Integer, ArrayList<Marker>>() {{
            put(0, markers);
        }});

        boolean result = plot.removeDomainMarker(0, marker, Layer.FOREGROUND, true);

        Assert.assertFalse(result);
        Assert.assertEquals(0, plot.getForegroundDomainMarkers().get(0).size());
        verify(plot, times(0)).fireChangeEvent();
    }

    @Test
    public void testRemoveDomainMarker_LayerIsBackground_MarkerExists_NotifyTrue() {
        ArrayList<Marker> markers = new ArrayList<>();
        Marker marker = mock(Marker.class);
        markers.add(marker);
        plot.setBackgroundDomainMarkers(new HashMap<Integer, ArrayList<Marker>>() {{
            put(0, markers);
        }});

        boolean result = plot.removeDomainMarker(0, marker, Layer.BACKGROUND, true);

        Assert.assertTrue(result);
        Assert.assertEquals(0, plot.getBackgroundDomainMarkers().get(0).size());
        verify(plot, times(1)).fireChangeEvent();
    }

    @Test
    public void testRemoveDomainMarker_LayerIsBackground_MarkerExists_NotifyFalse() {
        ArrayList<Marker> markers = new ArrayList<>();
        Marker marker = mock(Marker.class);
        markers.add(marker);
        plot.setBackgroundDomainMarkers(new HashMap<Integer, ArrayList<Marker>>() {{
            put(0, markers);
        }});

        boolean result = plot.removeDomainMarker(0, marker, Layer.BACKGROUND, false);

        Assert.assertTrue(result);
        Assert.assertEquals(0, plot.getBackgroundDomainMarkers().get(0).size());
        verify(plot, times(0)).fireChangeEvent();
    }

}