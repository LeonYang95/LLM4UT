# Running Examples of Our Study.

## Prompt Design

### Natural Language Description

Below is an example prompt used for DeepSeek-Coder models.

    ### Instruction:
    Your Task is to write some unit tests, and the method you are going to test is at the end of the instruction.
    
    The focal method belongs to the class `org.jfree.data.DefaultKeyedValues2D`, and the constructors are:
    ```
    public DefaultKeyedValues2D(boolean sortRowKeys);
    public DefaultKeyedValues2D(); 
    ```
    These are the fields defined in the class:
    ```
    private static final long serialVersionUID = -5514169970951994748L;
    private boolean sortRowKeys;
    ...
    ```
    These are the methods defined in the class :
    ```
    public List getColumnKeys();
    public void setValue(Number value, Comparable rowKey, Comparable columnKey);
    public void removeColumn(int columnIndex);
    public void removeRow(int rowIndex);
    ...
    ```
    This is the method that you are going to test.
    ```
    public void removeColumn(Comparable columnKey) {
        ...
    }
    ```
    The parameter of the method is `columnKey`.
    The parameters come from class `Comparable`.
    Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.
    
    ### Response:
    ```java
    import org.junit.Test;
    import org.junit.Assert;
    import org.junit.Before;
    。。。
    import org.jfree.chart.util.ObjectUtilities;
    import org.jfree.chart.util.PublicCloneable;
    
    public class DefaultKeyedValues2DTest{


### Code Language Description

Below is an example prompt used for DeepSeek-Coder models.


    ### Instrucion
    Your Task is to write some unit tests, and the method you are going to test is at the end of the instruction.
    ```
    // The method belongs to the class:
    org.jfree.data.DefaultKeyedValues2D
    
    // Fields
    private static final long serialVersionUID = -5514169970951994748L;
    private boolean sortRowKeys;
    ...
    
    // Other methods
    public List getColumnKeys();
    public void setValue(Number value, Comparable rowKey, Comparable columnKey);
    public void removeColumn(int columnIndex);
    public void removeRow(int rowIndex);
    ...
    
    // The following code is the method that you are going to test.
    public void removeColumn(Comparable columnKey) {
        ...
    }
    
    // The parameter of the method:
    columnKey
    
    // The parameters come from:
    Comparable
    ```
    Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.
    
    ### Response:
    ```java
    import org.junit.Test;
    import org.junit.Assert;
    import org.junit.Before;
    ...
    import org.jfree.chart.util.ObjectUtilities;
    import org.jfree.chart.util.PublicCloneable;
    
    public class DefaultKeyedValues2DTest{


## Prompt with In-Context-Learning Techniques.


Below is an example prompt used for DeepSeek-Coder model using CoT and code language description. 

For the target method `removeDomainMarker`, the LLM is intructed to summarize the intension of the method and then generate unit tests.

````
### Instruction:
Your Task is to write some unit tests. Please first understand the intent of the target method, the method you are going to test is at the end of the instruction.
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
public CategoryAnchor getDomainGridlinePosition();
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
### Response:
<The intention inferred by LLM>

### Instruction:
<The intention inferred by LLM>

You are a professional who writes Java test methods. Please write some unit tests for the removeDomainMarker method with the given intention.
You should write unit tests with maximizing both branch and line coverage. Please use Java 1.7 and Junit 4 and make sure that the output format is Markdown, and no explainations needed.

### Response:
```java
import org.junit.Test;
import org.junit.Assert;
import org.junit.Before;
import org.junit.After; 
...

public class CategoryPlotTest{
````



### Retrieval-Augmented Generation (RAG)

Below is an example prompt used for DeepSeek-Coder model using RAG and natural language description. 

For the target method `removeColumn`, the retrieved example is the method `previous` and its unit test `testW52Y9999Previous`.

````
### Instruction:
Your Task is to write some unit tests, and the method you are going to test is at the end of the instruction.

The focal method belongs to the class `org.jfree.data.DefaultKeyedValues2D`, and the constructors are:
```
public DefaultKeyedValues2D(boolean sortRowKeys);
public DefaultKeyedValues2D(); 
```
These are the fields defined in the class:
```
private static final long serialVersionUID = -5514169970951994748L;
private boolean sortRowKeys;
...
```
These are the methods defined in the class :
```
public List getColumnKeys();
public void setValue(Number value, Comparable rowKey, Comparable columnKey);
public void removeColumn(int columnIndex);
public void removeRow(int rowIndex);
...
```
Here is an example of a similar focal method and its unit test:
```
// The following code is an example focal method.
public RegularTimePeriod previous() {
		...
}
// The following code is the cooresponding unit test generated for the example method.
public void testW52Y9999Previous() {
		Week previous = (Week) this.w52Y9999.previous();
		assertEquals(this.w51Y9999, previous);
}
```

This is the method that you are going to test.
```
public void removeColumn(Comparable columnKey) {
    ...
}
```
The parameter of the method is `columnKey`.
The parameters come from class `Comparable`.
Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.

### Response:
```java
import org.junit.Test;
import org.junit.Assert;
import org.junit.Before;
...
import org.jfree.chart.util.ObjectUtilities;
import org.jfree.chart.util.PublicCloneable;

public class DefaultKeyedValues2DTest{
````


## Illustration Examples of Reasons of Undetected Defects.

<style>
  .container {
    display: flex;
    width: 100%;
  }
  .column {
    flex: 1;
    padding: 10px;
    box-sizing: border-box;
  }
</style>





### 1) Insufficient Test Coverage

<div class="container">
  <div class="column">

#### Code diff

The code diff of bug_id `JacksonDatabind_34` between the buggy and fixed versions: 

```diff
@Override
public void acceptJsonFormatVisitor(JsonFormatVisitorWrapper visitor, JavaType typeHint) throws JsonMappingException
{
    if (_isInt) {
        visitIntFormat(visitor, typeHint, JsonParser.NumberType.BIG_INTEGER);
 
    } else {
        Class<?> h = handledType();
        if (h == BigDecimal.class) {
-            visitFloatFormat(visitor, typeHint, JsonParser.NumberType.BIG_INTEGER);
+            visitFloatFormat(visitor, typeHint, JsonParser.NumberType.BIG_DECIMAL);
        } else {
            // otherwise bit unclear what to call... but let's try:
            /*JsonNumberFormatVisitor v2 =*/ visitor.expectNumberFormat(typeHint);
        }
    }
}

```


#### Explanation

The generated unit test does not **cover** the branch `h == BigDecimal.class`

the To detect this bug, the unit test should construct the `NumberSerializer` object as the `BigDecimal.class`.



  </div>
  <div class="column">



#### Unit Test
The test case generated by `CL-7B`(CodeLlama-7B-Instruct): 

```java
public class LLMGeneratedTests {

private NumberSerializer numberSerializer;
private JavaType typeHint;
private JsonFormatVisitorWrapper visitor;

@Test(expected = NullPointerException.class)
    public void testAcceptJsonFormatVisitorWithNullTypeHint() throws JsonMappingException {
        numberSerializer.acceptJsonFormatVisitor(visitor, null);
    }
       
    @Test
    public void testAcceptJsonFormatVisitorForOther() throws JsonMappingException {
        numberSerializer = new NumberSerializer(Number.class);
        numberSerializer.acceptJsonFormatVisitor(visitor, typeHint);
        verify(visitor).expectNumberFormat(typeHint);
    }
    
    @Test(expected = NullPointerException.class)
    public void testAcceptJsonFormatVisitorWithNullVisitor() throws JsonMappingException {
        numberSerializer.acceptJsonFormatVisitor(null, typeHint);
    }
    
    @Before
    public void setUp() {
        numberSerializer = new NumberSerializer(Number.class);
        visitor = mock(JsonFormatVisitorWrapper.class);
        typeHint = mock(JavaType.class);
    }
    
}
```



</div>
</div>


### 2) Missing Specific Inputs

<div class="container">
  <div class="column">

#### Code diff

The code diff of bug_id `Gson_8` between the buggy and fixed versions: 

```diff
public static UnsafeAllocator create() {
    // try JVM
    // public class Unsafe {
    //   public Object allocateInstance(Class<?> type);
    // }
    try {
        Class<?> unsafeClass = Class.forName(\"sun.misc.Unsafe\");
        Field f = unsafeClass.getDeclaredField(\"theUnsafe\");
        f.setAccessible(true);
        final Object unsafe = f.get(null);
        final Method allocateInstance = unsafeClass.getMethod(\"allocateInstance\", Class.class);
        return new UnsafeAllocator() {
        
            @Override
            @SuppressWarnings(\"unchecked\")
            public <T> T newInstance(Class<T> c) throws Exception {
+                assertInstantiable(c);
                return (T) allocateInstance.invoke(unsafe, c);
            }
        };
    } catch (Exception ignored) {
    }
    // try dalvikvm, post-gingerbread
    // public class ObjectStreamClass {
    //   private static native int getConstructorId(Class<?> c);
    //   private static native Object newInstance(Class<?> instantiationClass, int methodId);
    // }
    try {
        Method getConstructorId = ObjectStreamClass.class.getDeclaredMethod(\"getConstructorId\", Class.class);
        getConstructorId.setAccessible(true);
        final int constructorId = (Integer) getConstructorId.invoke(null, Object.class);
        final Method newInstance = ObjectStreamClass.class.getDeclaredMethod(\"newInstance\", Class.class, int.class);
        newInstance.setAccessible(true);
        return new UnsafeAllocator() {
        
            @Override
            @SuppressWarnings(\"unchecked\")
            public <T> T newInstance(Class<T> c) throws Exception {
                assertInstantiable(c);
                return (T) newInstance.invoke(null, c, constructorId);
            }
        };
    } catch (Exception ignored) {
    }
    // try dalvikvm, pre-gingerbread
    // public class ObjectInputStream {
    //   private static native Object newInstance(
    //     Class<?> instantiationClass, Class<?> constructorClass);
    // }
    try {
        final Method newInstance = ObjectInputStream.class.getDeclaredMethod(\"newInstance\", Class.class, Class.class);
        newInstance.setAccessible(true);
        return new UnsafeAllocator() {
        
            @Override
            @SuppressWarnings(\"unchecked\")
            public <T> T newInstance(Class<T> c) throws Exception {
+                assertInstantiable(c);
                return (T) newInstance.invoke(null, c, Object.class);
            }
        };
    } catch (Exception ignored) {
    }
    // give up
    return new UnsafeAllocator() {
    
        @Override
        public <T> T newInstance(Class<T> c) {
            throw new UnsupportedOperationException(\"Cannot allocate \" + c);
        }
    };
}

```
  </div>
  <div class="column">


#### Unit Test
The test case generated by `CL-7B`(CodeLlama-7B-Instruct): 

```java
public class LLMGeneratedTests {
    @Test
    public void testCreate() {
        UnsafeAllocator allocator = UnsafeAllocator.create();
        Assert.assertNotNull(allocator);
    }

    @Test
    public void testNewInstanceWithException() {
        UnsafeAllocator allocator = UnsafeAllocator.create();
        Assert.assertNotNull(allocator);
        try {
            allocator.newInstance(null);
            Assert.fail(\"Expected exception not thrown\");
        } catch (Exception e) {
            Assert.assertTrue(e instanceof NullPointerException);
        }
    }
}
```

#### Explanation

Although the unit test covers the buggy code lines, it does not detect the bug because of missing specific inputs.

To detect this bug, the **input** to `allocator.newInstance()` in the unit test should be the `Interface` class, not just the `null` class provided in the generated unit test.

</div>
</div>



### 3) Improper Assertion

<div class="container">
  <div class="column">

#### Code diff

The code diff of bug_id `Chart_3` between the buggy and fixed versions: 

```diff
public TimeSeries createCopy(int start, int end)
            throws CloneNotSupportedException {
        if (start < 0) {
            throw new IllegalArgumentException("Requires start >= 0.");
        }
        if (end < start) {
            throw new IllegalArgumentException("Requires start <= end.");
        }
        TimeSeries copy = (TimeSeries) super.clone();
+        copy.minY = Double.NaN;
+        copy.maxY = Double.NaN;
        copy.data = new java.util.ArrayList();
        if (this.data.size() > 0) {
            for (int index = start; index <= end; index++) {
                TimeSeriesDataItem item
                        = (TimeSeriesDataItem) this.data.get(index);
                TimeSeriesDataItem clone = (TimeSeriesDataItem) item.clone();
                try {
                    copy.add(clone);
                }
                catch (SeriesException e) {
                    e.printStackTrace();
                }
            }
        }
        return copy;
    }
```

#### Explanation

To detect this bug, the unit test should set up **assertions** to check the values of `copy.minY` and `copy.maxY`.

  </div>
  <div class="column">


#### Unit Test
The test case generated by `PD-34B`(Phind-CodeLlama-34B-v2): 

```java
public class LLMGeneratedTests {

    private TimeSeries series;
    private RegularTimePeriod period;
    private TimeSeries seriesCopy;
    private static final double DELTA = 0.0000001;
    private TimeSeriesDataItem item;
    
    @Test
    public void testCreateCopyWithMultipleItems() throws CloneNotSupportedException {
        series.add(item);
        series.add(new TimeSeriesDataItem(new Day(2, 1, 2000), 200.0));
        seriesCopy = series.createCopy(0, 1);
        assertEquals(2, seriesCopy.getItemCount());
        assertEquals(series.getTimePeriod(0), seriesCopy.getTimePeriod(0));
        assertEquals(series.getValue(0), seriesCopy.getValue(0));
        assertEquals(series.getTimePeriod(1), seriesCopy.getTimePeriod(1));
        assertEquals(series.getValue(1), seriesCopy.getValue(1));
    }
    
    
    @Test(expected = IllegalArgumentException.class)
    public void testCreateCopyWithNegativeStart() throws CloneNotSupportedException {
        series.createCopy(-1, 0);
    }
    
    
    @Test
    public void testCreateCopyWithNoItems() throws CloneNotSupportedException {
        seriesCopy = series.createCopy(0, 0);
        assertEquals(0, seriesCopy.getItemCount());
    }
    
    
    @Test(expected = IllegalArgumentException.class)
    public void testCreateCopyWithEndLessThanStart() throws CloneNotSupportedException {
        series.createCopy(1, 0);
    }
    
    
    @Before
    public void setUp() {
        series = new TimeSeries(\"Test Series\");
        seriesCopy = new TimeSeries(\"Test Series Copy\");
        item = new TimeSeriesDataItem(new Day(1, 1, 2000), 100.0);
        period = new Day();
    }
    
    
    @Test
    public void testCreateCopyWithSomeItemsOutOfRange() throws CloneNotSupportedException {
        series.add(item);
        series.add(new TimeSeriesDataItem(new Day(2, 1, 2000), 200.0));
        seriesCopy = series.createCopy(1, 1);
        assertEquals(1, seriesCopy.getItemCount());
        assertEquals(series.getTimePeriod(1), seriesCopy.getTimePeriod(0));
        assertEquals(series.getValue(1), seriesCopy.getValue(0));
    }
    
    
    @Test
    public void testCreateCopy() throws CloneNotSupportedException {
        series.add(item);
        seriesCopy = series.createCopy(0, 0);
        assertEquals(series.getItemCount(), seriesCopy.getItemCount());
        assertEquals(series.getTimePeriod(0), seriesCopy.getTimePeriod(0));
        assertEquals(series.getValue(0), seriesCopy.getValue(0));
    }
}
```
  </div>
</div>




